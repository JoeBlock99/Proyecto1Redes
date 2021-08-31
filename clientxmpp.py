from constants import XMPP_DOMAIN
from helpers import index_of_list, required_input
import logging
import json
import slixmpp
from slixmpp import XMLStream
import time
import signal
import threading
import sys
import ssl
from threading import Thread
from dijstra import nextNode, recipients


class Client(slixmpp.ClientXMPP):

    """
    A basic Slixmpp bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, user, password):
        slixmpp.ClientXMPP.__init__(self, user, password)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.user = user
        p = user.find("@")
        if p > -1:
            self.d_user = user[:p]
        else:
            self.d_user = user

        self.password = password
        self.started = 0
        self.inited = False
        # self.add_event_handler("presence_subscribe", self.presence_subscribed)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)  # flag de register
        self.add_event_handler('message', self.message)
        # self.send_tables()

    @property
    def recipents(self):
        recipents_array = []
        for n in recipients(self.d_user):
            recipents_array.append(n)
        return recipents_array

    def compute_username(self, name):
        return name.lower() + "@" + XMPP_DOMAIN

    def presence_subscribed(self, new_presence):
        item = self.roster[new_presence['to']][new_presence['from']]
        item.authorize()
        item.subscribe()

    def signal_handler(self, a, b):
        self.disconnect(wait=True)
        self.started = -1
        sys.exit(0)

    def get_recipent(self):
        recipent_index = index_of_list(
            self.recipents, "Ingrese a quien le desea enviar un mensaje: "
        )
        return self.recipents[recipent_index]

    def message(self, msg):
        print("\n")
        if msg['type'] in ('chat'):
            message_json = json.loads(msg["body"])
            if "to" in message_json:
                if message_json["to"] == self.d_user:
                    print("Se recibe mensaje de: ", message_json["from"])
                    print(message_json["message"])
                else:
                    # self.node.get_next_node(message_json["to"])
                    destinatary = nextNode(self.d_user, message_json["to"])
                    if destinatary is None:
                        destinatary = message_json["to"]

                    message = "El mensaje que esta pensado llegar a: " + \
                        message_json["to"] + " esta pasando por " + \
                        self.d_user + " y se dirige hacia " + destinatary
                    print(message)
                    self.make_message(mto=self.compute_username(message_json["from"]).lower(
                    ), mbody=json.dumps({"message": message}), mtype="chat").send()

                    self.make_message(mto=self.compute_username(destinatary).lower(),
                                      mbody=msg["body"],
                                      mtype='chat').send()
            else:
                print("Imprimamos", message_json["message"])

        self.get_roster()

    async def start(self, event):
        self.inited = True
        self.send_presence()
        print("conectado")
        while True:
            try:
                # Ask for roster
                await self.get_roster()
                self.started = 1
            except:
                self.started = -1
                self.disconnect()
                print("todo mal")
            # await self.get_roster()

    async def register(self, iq):
        resp = self.Iq()
        resp['type'] = 'set'
        resp['register']['username'] = self.boundjid.user
        resp['register']['password'] = self.password
        await resp.send()
        logging.info("Account created for %s!" % self.boundjid)

    # 1 to 1 message
    '''def sendTableMessage(self, to, message):

        self.make_message(mto=to,
                          mbody=message,
                          mtype='normal',
                          mfrom=self.boundjid.bare
                          ).send()'''

    # 1 to 1 message

    # def sendMessage(self, to, r):

    def logOut(self):
        self.started = -1
        self.disconnect(wait=True)
