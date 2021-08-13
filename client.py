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
        
        self.add_event_handler("session_start", self.start)#es como una flag de que se inicio sesion
        self.add_event_handler("register", self.register)#flag de register
        
    async def start(self, event):
       
        self.send_presence()# manda nuestra informacion
        await self.get_roster() # recive la informacion que hay en el server relacionada a nosotros
        showMenu = True
        while(showMenu):
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
                to = input("Username: ")
                to = to +"@alumchat.xyz"
                self.sendNotification(to)
                self.sendMessage(to)
            elif(menu == 2):
                self.sendFile()
            elif(menu == 3):
                self.groupChat()
            elif(menu == 4):
                self.addContact()
            elif(menu == 5):
                self.userDetail()
            elif(menu == 6):
                self.listUsers()
            elif(menu == 7):
                self.status()
            elif(menu == 8):
                self.logOut()
                showMenu = False
            elif(menu == 9):
                self.deleteUser()
                showMenu = False
            await self.get_roster()
            
        
    def status(self):
        print("""------------Options------------\n
                1. Available
                2. Not available
                3. Do not disturb""")
        option = int(input("Selected number: "))
        if(option == 1):
            self.send_presence(pshow="chat", pstatus="Available")
        elif(option == 2):
            self.send_presence(pshow="away", pstatus="Not available")
        elif(option == 3):
            self.send_presence(pshow="dnd", pstatus="Do not disturb")
        else:
            self.status()
        
    def groupChat(self):
        self.register_plugin('xep_0030')
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0199')

        room = input("Group name: ")
        nickname = input("Nickname: ")
        message = input('Message: ')
        self.plugin['xep_0045'].join_muc(room+"@conference.alumchat.xyz", nickname)
        self.send_message(mto=room+"@conference.alumchat.xyz", mbody=message, mtype='groupchat')

    async def register(self,iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        await resp.send()
        logging.info("Account created for %s!" % self.boundjid)    

    # En el momento en el que se manda el mensaje se activa esta notificacion
    def sendNotification(self, to):
        notification = self.Message()
        notification["chat_state"] = "composing"
        notification["to"] = to
        notification.send()

    # 1 to 1 message
    def sendMessage(self,to):
        message = input("Message: ")
        self.send_message(mto=to,
                          mbody=message,
                          mtype='chat')
        
    def userDetail(self):
        self.get_roster()
        detail = input("Username: ")
        detail = detail+"@alumchat.xyz"
        usrDet = self.client_roster[detail]# users name that no one is using
        state = self.client_roster.presence(detail)
        print('-' * 72)
        for res, pres in state.items():
            show = 'available'
            if pres['show']:
                show = pres['show']
            print('   - %s (%s)' % (res, show))
            if pres['status']:
                print('       %s(%s)' % (detail,pres['status']))
                print('-' * 72)

    def addContact(self):
        newContact = input("Contact username: ")
        newContact = newContact+"@alumchat.xyz"
        self.send_presence_subscription(pto=newContact)
        self.send_message(mto=newContact, mbody="Hola", mtype="chat", mfrom=self.boundjid.bare)
        
    
    def logOut(self):
        self.disconnect()
        
    
    def listUsers(self):
        print('Roster for %s' % self.boundjid.bare)
        groups = self.client_roster.groups()
        for group in groups:
            print('\n%s' % group)
            print('-' * 72)
            for jid in groups[group]:
                name = self.client_roster[jid]['name']
                if self.client_roster[jid]['name']:
                    print(' %s (%s)' % (name, jid))
                else:
                    print('\n',jid)

                connections = self.client_roster.presence(jid)
                for res, pres in connections.items():
                    show = 'available'
                    if pres['show']:
                        show = pres['show']
                    print('   - %s (%s)' % (res, show))
                    if pres['status']:
                        print('       %s' % pres['status'])
                        print('-' * 72)
    #delete logged user
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
        xmpp.register_plugin('xep_0085')
        xmpp['xep_0077'].force_registration = True
        xmpp.connect()
        xmpp.process()
    elif(opcion == 2):
        user = input("Username: ")
        password = input("Password: ")
        xmpp = Client(user+"@alumchat.xyz", password)
        xmpp.register_plugin('xep_0030') # Service Discovery
        xmpp.register_plugin('xep_0199') # XMPP Ping
        xmpp.register_plugin('xep_0085')
        xmpp.connect()
        xmpp.process(forever=False)
    elif(opcion == 3):
        exit()
    else:
        exit()
    
