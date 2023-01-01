"""
Created on Tue Jul 22 00:47:05 2014

@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import secure


class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        # self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        # self.sonnet = pkl.load(self.sonnet_f)
        # self.sonnet_f.close()
        self.sonnet = indexer.PIndex("AllSonnets.txt")

        self.user_list = {}
        try:
            i_list = open("secret.pk","rb")
            self.user_list = pkl.load(i_list)
        except:
            self.user_list = {}
        self.public_key, self.private_key = secure.generate_keys()
        self.peers_keys = {} #users public_key

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def legal_name(self, name):
        ok = len(name)<7
        for word in name:
            if word in string.punctuation+" ":
                ok = False
        return ok



    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            print("login:", msg)
            if len(msg) > 0:
                Flag = False

                if msg["action"] == "tourist":
                    name = msg["name"]

                    if self.group.is_member(name) or name in self.user_list and self.legal_name(name[3:]):  
                        # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "tourist", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                    elif not self.legal_name(name[3:]):
                        #illegal name
                        mysend(sock, json.dumps(
                            {"action": "tourist", "status": "illegal"}))
                        print(name + ' illegal name attempt')

                    else:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
                        self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "tourist", "status": "ok"}))
                        Flag = True


                elif msg["action"] == "Continue":
                    name = msg["name"]

                    if name in self.user_list and msg["pwd"]==self.user_list[name]:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name+'.idx', 'rb'))
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "Continue", "status": "ok"}))
                        Flag = True
                    elif name not in self.user_list:
                        mysend(sock, json.dumps(
                            {"action": "Continue", "status": "not found"}))
                        print(name + ' empty login attempt')
                    else:
                        mysend(sock, json.dumps(
                            {"action": "Continue", "status": "wrong pwd"}))
                        print(name + ' wrong pwd login attempt')


                elif msg["action"] == "register":
                    name = msg["name"]

                    if self.group.is_member(name) or name in self.user_list:
                        # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "register", "status": "duplicate"}))
                        print(name + ' duplicate register attempt')
                    elif not self.legal_name(name):
                        # illegal name
                        mysend(sock, json.dumps(
                            {"action": "register", "status": "illegal"}))
                        print(name + ' illegal name attempt')
                    else:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
                        if name not in self.indices.keys():
                            try:
                                self.indices[name] = pkl.load(
                                    open(name+'.idx', 'rb'))
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        print(name + ' register an account')
                        self.user_list[name]=msg["pwd"]

                        user_data = open("secret.pk","wb")
                        pkl.dump(self.user_list, user_data)
                        user_data.close()

                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "register", "status": "ok"}))
                        Flag = True

                    
                else:
                    print('wrong code received')
                
                if Flag:
                    print("send to each user the current users...")
                    sd_msg = ""
                    for user in self.group.members.keys():
                        sd_msg += user + ","
                    for user in self.group.members.keys():
                        mysend(self.logged_name2sock[user],json.dumps(
                            {"action": "new_client", "users":sd_msg[:-1]}
                        ))
                    mysend(sock,json.dumps(
                        {"action": "key", "public key": self.private_key}
                    ))


                
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
        if name[:3] != "[T]":
            pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
        del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        print(msg)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)


            elif msg["action"] == "key":
                from_name=self.logged_sock2name[from_sock]
                self.peers_keys[from_name] = msg["public key"]
                print(from_name, "'s key is", msg["public key"])
                mysend(from_sock, json.dumps(
                    {"action":"key", "public key": self.public_key}
                ))
            elif msg["action"] == "reset":
                from_name=self.logged_sock2name[from_sock]
                self.peers_keys.pop(from_name)
# ==============================================================================
# handle messeage exchange: one peer for now. will need multicast later
# ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                said1 = secure.decrypt(self.private_key,msg["message"])
                said2 = text_proc(said1, from_name)
                self.indices[from_name].add_msg_and_index(said2)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    said3 = secure.encrypt(said1,self.peers_keys[g])
                    mysend(to_sock, json.dumps(
                        {"action": "exchange", "from": msg["from"], "message":said3}))
# ==============================================================================
#                 listing available peers
# ==============================================================================
            elif msg["action"] == "list":
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all()
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
# ==============================================================================
#             retrieve a sonnet
# ==============================================================================
            elif msg["action"] == "poem":
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = '\n'.join(poem).strip()
                print('here:\n', poem)
                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
#                 search
# ==============================================================================
            elif msg["action"] == "search":
               term = msg["target"]
               from_name = self.logged_sock2name[from_sock]
               print('search for ' + from_name + ' for ' + term)
               # search_rslt = (self.indices[from_name].search(term))
               search_rslt = '\n'.join(
                   [x[-1] for x in self.indices[from_name].search(term)])
               print('server side search: ' + search_rslt)
               mysend(from_sock, json.dumps(
                   {"action": "search", "results": search_rslt}))
# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps({"action": "disconnect"}))
# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================
    def run(self):
        print('starting server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            for newc in self.new_clients[:]:
                if newc in read:
                    self.login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()
