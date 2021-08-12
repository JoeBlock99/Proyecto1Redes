#!/usr/bin/env python3

# Slixmpp: The Slick XMPP Library
# Copyright (C) 2010  Nathanael C. Fritz
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.

import logging
from getpass import getpass
from argparse import ArgumentParser

import slixmpp


class Client(slixmpp.ClientXMPP):

    """
    A basic Slixmpp bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, user, password):
        slixmpp.ClientXMPP.__init__(self, user, password)

        self.user = user
        self.password = password
        
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)
        
    async def start(self, event):
       
        self.send_presence()
        await self.get_roster()

        self.menu()

    def menu(self):
        print("""=============================BIENVENID@=============================\n\n\n 
                    Menu:\n
                    1. Send message\n
                    2. Send file\n
                    3. Send group message\n
                    4. Add to contacts\n
                    5. User detail\n 
                    6. List Users\n
                    7. Status update\n
                    8. Log-out\n
                    9. Delete user\n
                    """)                   
        menu = int(input("Selected number: "))
        if(menu == 1):
            self.sendMessage()
        elif(menu == 2):
            pass
        elif(menu == 3):
            pass
        elif(menu == 4):
            self.addContact()
        elif(menu == 5):
            pass
        elif(menu == 6):
            pass
        elif(menu == 7):
            self.status()
        elif(menu == 8):
            self.logOut()
        elif(menu == 9):
            self.deleteUser()
        else:
            self.menu()
    def status(self, status):
        print("""------------Options------------\n
                1. Available
                2. Not available
                3. Do not disturb""")
        option = int(input("Selected number: "))
        if(option == 1):
            self.send_presence(pshow="Available", pstatus=status)
        elif(option == 2):
            self.send_presence(pshow="Not available", pstatus=status)
        elif(option == 3):
            self.send_presence(pshow="Do not disturb", pstatus=status)
        else:
            self.status()


    async def register(self,iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        await resp.send()
        logging.info("Account created for %s!" % self.boundjid)    

    def sendMessage(self):
        to = input("To: ")
        message = input("Message: ")
        self.send_message(mto=to+"@alumchat.xyz",
                          mbody=message,
                          mtype='chat')
        self.menu()

    def addContact(self):
        newContact = input("Contact username: ")
        self.send_presence_subscription(pto=newContact+"@alumchat.xyz")
        self.send_message(mto=newContact, mbody="Hola", mtype="chat", mfrom=self.boundjid.bare)
    
    def logOut(self):
        self.disconnect()
    
    def deleteUser(self):
        self.register_plugin("xep_0030")
        self.register_plugin("xep_0004")
        self.register_plugin("xep_0199")
        self.register_plugin("xep_0066")
        self.register_plugin("xep_0077")
        delete = self.Iq()
        delete['type'] = 'set'
        delete['from'] = self.boundjid.user
        delete['register']['remove'] = True
        delete.send()
        print("DELETED")
        self.disconnect()


if __name__ == '__main__':
    # Setup logging.
    logging.basicConfig(level=logging.DEBUG, 
    format='%(levelname)-8s %(message)s')
    print("""\n================================MENU================================\n\n 
                    1. Register\n
                    2. Log-in\n
                    3. STOP\n
                    """)
    opcion = int(input("La opcion a escoger: "))
    if(opcion == 1):
        user = input("Username: ")
        password = input("Password: ")
        xmpp = Client(user+"@alumchat.xyz",password)
        xmpp.register_plugin('xep_0004') # Data forms
        xmpp.register_plugin('xep_0066') # Out-of-band Data
        xmpp.register_plugin('xep_0077')
        xmpp['xep_0077'].force_registration = True
        xmpp.connect()
        xmpp.process()
    elif(opcion == 2):
        user = input("Username: ")
        password = input("Password: ")
        xmpp = Client(user+"@alumchat.xyz", password)
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0199') # XMPP Ping
        xmpp.connect()
        xmpp.process(forever=False)
    elif(opcion == 3):
        exit()
    else:
        exit()
    
