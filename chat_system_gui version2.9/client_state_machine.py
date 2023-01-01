"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import os
os.environ["PYGAME_SUPPORT_PROMPT"]="hide"
import pygame
import secure
import indexer

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.peer_key=() #server pub_key
        self.public_key=()
        self.private_key=()
        self.indices={}



    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def gaming_to(self, peer):
        msg = json.dumps({"action":"connect_g", "target":peer})
        mysend(self.s, msg)

        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are gaming with '+ self.peer + ', good luck! \n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot gaming with yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)



    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def reset_keys(self):
        self.public_key=()
        self.private_key=()
        self.peer_key=()

    
    #def set_indexing(self):
    #    if self.me not in self.indices.keys():
    #        try:
    #            self.indices[self.me] = pkl.load(open(self.me+".idx",'rb'))
    #        except IOError:
    #            self.indices[self.me] = indexer.Index(self.me)
    
    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
        

#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'game1':
                    self.state = S_GAMING
                    os.system("python Tic-Tac-Toe.py")
                    self.state = S_LOGGEDIN
                elif my_msg == 'game2':
                    self.state = S_GAMING
                    os.system("python Snake.py")
                    self.state = S_LOGGEDIN
                elif my_msg == 'game3':
                    self.state = S_GAMING
                    os.system("python mine1.0.py")
                    self.state = S_LOGGEDIN
                    
                # elif my_msg[0] == 'g':
                #     peer = my_msg[1:]
                #     peer = peer.strip()
                #     if self.gaming_to(peer) == True:
                #         self.state = S_GAMING
                #         self.out_msg += 'Gaming with ' + peer + '. Good luck!\n\n'
                #         self.out_msg += '-----------------------------------\n'
                #     else:
                #         self.out_msg += 'Connection unsuccessful\n'
                
                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                        self.public_key,self.private_key = secure.generate_keys()
                        mysend(self.s,json.dumps({"action":"key","public key":self.public_key}))
                        self.out_msg += "send the key successfully\n"
                        response = json.loads(myrecv(self.s))
                        self.peer_key = response["public key"] #save server's public_key
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    self.public_key,self.private_key = secure.generate_keys()
                    mysend(self.s,json.dumps({"action":"key","public key":self.public_key}))
                    self.out_msg += "send the key successfully\n"
                    response = json.loads(myrecv(self.s))
                    self.peer_key = response["public key"] #save server's public_key

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:

    
            if len(my_msg) > 0:     # my stuff going out
                msg=secure.encrypt(my_msg,self.peer_key)
                mysend(self.s, json.dumps({"action":"exchange", "from":self.me, "message":msg}))
                self.out_msg+=self.me+": "+my_msg+"\n"
                if my_msg == 'bye':
                    mysend(self.s,json.dumps({"action" :"reset"}))
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    self.reset_keys()

            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg["action"] == "exchange":
                    #msg = secure.decrypt(peer_msg["message"], self.peer_key)
                    msg = secure.decrypt(self.private_key, peer_msg["message"])
                    self.out_msg += "Encrypted message:" + peer_msg['message'] +'\n'
                    self.out_msg +=  peer_msg["from"] + ": "+ msg
                   
                elif peer_msg["action"] == "reset":
                    self.reset_keys()
                    pass

        elif self.state == S_GAMING:  
            if len(my_msg) > 0:
                print("message: ", my_msg)
                mysend(self.s, json.dumps({"action":"exchange_g", "from":self.me + ": ", "message":my_msg}))

                if my_msg == 'n' or my_msg == 'q' or my_msg == 'Q':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    
            if len(peer_msg) > 0: 
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)"
                elif peer_msg["action"] == "disconnect":
                    self.out_msg += peer_msg["message"]
                    self.state = S_LOGGEDIN
                else:
                    self.out_msg += peer_msg["from"] +": " + peer_msg["message"]

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += "welcome back...\n\n"
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
