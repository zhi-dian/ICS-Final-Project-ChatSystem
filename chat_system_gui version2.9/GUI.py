#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 13:36:58 2021

@author: bing
"""

# import all the required  modules
import threading
import select
from tkinter import *
from tkinter import font
from tkinter import ttk
from chat_utils import *
import json

# GUI class for the chat


class GUI:
    # constructor method
    def __init__(self, send, recv, sm, s):
        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.send = send
        self.recv = recv
        self.sm = sm
        self.socket = s
        self.my_msg = ""
        self.system_msg = ""
        self.Buttons = []
        self.users = []

    def login_error(self,msg):
        self.error_msg.destroy()
        self.error_msg = Label(self.login,
                             text=msg,
                             fg="red",
                             font="Helvetica 14"
                             )
        self.error_msg.place(relx=0.15, 
                             rely=0.75)

    def login(self):
        # login window
        self.login = Toplevel()
        # set the title
        self.login.title("Login")
        self.login.resizable(width=False,
                             height=False)
        self.login.configure(width=500,
                             height=350)
        # create a Label
        self.pls = Label(self.login,
                         text="Please login to continue",
                         justify=CENTER,
                         font="Helvetica 14 bold")

        self.pls.place(relheight=0.15,
                       relx=0.2,
                       rely=0.07)


        # create a Label
        self.labelName = Label(self.login,
                               text="Name: ",
                               font="Helvetica 12")


        # create a entry box for
        # typing the message
        self.entryName = Entry(self.login,
                               font="Helvetica 14")


        # create a Lable for password
        self.labelPWD = Label(self.login,
                               text="Password: ",
                               font="Helvetica 12")

        # create a entry box for
        # typing the message
        self.entryPWD = Entry(self.login,
                               font="Helvetica 14",show="*")


        # arrange the interface
        self.labelName.place(relheight=0.12,
                             relx=0.1,
                             rely=0.2)
        self.entryName.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.2)
        self.labelPWD.place(relheight=0.12,
                             relx=0.1,
                             rely=0.4)
        self.entryPWD.place(relwidth=0.4,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.4)

        # set the focus of the curser
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.login,
                         text="CONTINUE",
                         font="Helvetica 14 bold",
                         command=lambda: self.Continue(self.entryName.get(),self.entryPWD.get()))
        self.reg = Button(self.login,
                         text="Register",
                         font="Helvetica 14 bold",
                         command=lambda: self.Register(self.entryName.get(),self.entryPWD.get()))
        self.tour = Button(self.login,
                         text="Tourist",
                         font="Helvetica 14 bold",
                         command=lambda: self.Tourist(self.entryName.get()))

        self.go.place(relx=0.4,
                      rely=0.55)
        self.reg.place(relx=0.1,
                      rely=0.55)
        self.tour.place(relx=0.7,
                      rely=0.55)
        
        self.error_msg = Label(self.login,
                             text="",
                             font="Helvetica 14 bold"
                             )
        self.error_msg.place(relx=0.15, 
                             rely=0.75)


        self.Window.mainloop()

    def Tourist(self, name):
        if len(name) > 0:
            name = "[T]"+ name
            msg = json.dumps({"action": "tourist", "name": name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                # the thread to receive messages
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
            elif response["status"] == 'duplicate':
                self.login_error("Name Already Exists")
            else:
                self.login_error("Name should less than 7 and no punctuation")
           

    def Continue(self, name, pwd):
        if len(name) > 0:
            msg = json.dumps({"action": "Continue", "name": name, "pwd": pwd})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
            elif response["status"] == 'wrong pwd':
                self.login_error("Wrong Password")
            else:
                self.login_error("No Such User")


    def Register(self, name, pwd):
        if len(name) > 0:
            msg = json.dumps({"action": "register", "name": name, "pwd": pwd})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.login.destroy()
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(name)
                process = threading.Thread(target=self.proc)
                process.daemon = True
                process.start()
                self.layout(name)
                self.textCons.config(state=NORMAL)
                # self.textCons.insert(END, "hello" +"\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)
            elif response["status"] == 'duplicate':
                self.login_error("Name Already Exists")
            else:
                self.login_error("Name should less than 7 and no punctuation")
           


    # The main layout of the chat
    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("CHATROOM")
        self.Window.resizable(width=False,
                              height=True)
        self.Window.configure(width=950,
                              height=550,
                              bg="#66ccff")
        self.labelHead = Label(self.Window,
                               bg="#b7b7b7",
                               fg="#EAECEE",
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1,
                            relheight=0.08)
        # self.line = Label(self.Window,
        #                   width=450,
        #                   bg="#ABB2B9")

        # self.line.place(relwidth=1,
        #                 rely=0.07,
        #                 relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#ccffff",
                             fg="Black",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.69,
                            relwidth=0.65,
                            rely=0.16)
        
        self.command = Label(self.Window,
                             text=menu,
                             anchor="nw",
                             justify="left",
                             bg="#ccffff",
                             fg="Black",
                             bd=4,
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.command.place(relheight=0.69,
                            relwidth=0.35,
                            rely=0.16,
                            relx=0.65)

        self.labelBottom = Label(self.Window,
                                 bg="#e1e1e1",
                                 height=60)

        self.labelBottom.place(relwidth=1,
                               rely=0.85)

        self.entryMsg = Entry(self.labelBottom,
                              bg="White",
                              fg="#111",
                              font="Helvetica 13")

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.74,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 16 bold",
                                width=20,
                                bg="#959595",
                                command=lambda: self.sendButton(self.entryMsg.get()))

        self.buttonMsg.place(relx=0.77,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    # function to basically start the thread for sending messages

    def sendButton(self, msg):
        # self.textCons.config(state=DISABLED)
        self.my_msg = msg
        # print(msg)
        self.entryMsg.delete(0, END)
        self.textCons.config(state=NORMAL)
        #self.textCons.insert(END, msg + "\n")
        self.textCons.config(state=DISABLED)
        self.textCons.see(END)

    def connect_to(self,target,i):
        # self.system_msg = self.sm.proc("bye", [])
        # self.system_msg = self.sm.proc("c "+target, [])
        print("the index is ", i)
        self.my_msg = "bye"
        print("leave the room successfully")
        print("connect to user", target, "...")
        self.my_msg = "c " + target

    def update_buttons(self, users):
        print("changing buttons")
        print(users)
        for btn in self.Buttons:
            btn.destroy()
        self.Buttons = []
        self.users = []
        for i in range(len(users)):
            self.users.append(users[i])
            self.Buttons.append(Button(self.Window,
                            text=users[i],
                            font="Helvetica 14",
                            bg="#d7d7d7",
                            command=lambda target = users[i]:self.connect_to(target,i)))
        
        rel_l = 1/len(self.Buttons)
        for i in range(len(self.Buttons)):  
            self.Buttons[i].place(relx=rel_l*i,
                                rely=0.08,
                                relheight=0.08,
                                relwidth=rel_l)


    def proc(self):
        # print(self.msg)
        while True:
            read, write, error = select.select([self.socket], [], [], 0)
            peer_msg = []
            # print(self.msg)
            if self.socket in read:
                peer_msg = self.recv()

                if json.loads(peer_msg)["action"] == "new_client":
                    print("receive signal to change buttons...")
                    peer_msg = json.loads(peer_msg)
                    self.update_buttons(peer_msg["users"].split(","))
                    peer_msg = []
            
            if len(self.my_msg) > 0 or len(peer_msg) > 0:
                # print(self.system_msg)
                self.system_msg = self.sm.proc(self.my_msg, peer_msg)
                self.my_msg = ""
                self.textCons.config(state=NORMAL)
                self.textCons.insert(END, self.system_msg + "\n\n")
                self.textCons.config(state=DISABLED)
                self.textCons.see(END)

    def run(self):
        self.login()


# create a GUI class object
if __name__ == "__main__":
 #   g = GUI()
    pass
