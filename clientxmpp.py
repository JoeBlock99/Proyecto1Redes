from constants import XMPP_DOMAIN
from node import Node, build_prod_nodes
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


class Client(slixmpp.ClientXMPP):

    """
    A basic Slixmpp bot that will log in, send a message,
    and then log out.
    """

    def __init__(self, user, password, nodes_dict):
        slixmpp.ClientXMPP.__init__(self, user, password)
        signal.signal(signal.SIGINT, self.signal_handler)
        self.nodes_dict = nodes_dict
        self.user = user
        p = user.find("@")
        if p > -1:
            self.d_user = user[:p]
        else:
            self.d_user = user
        self.inited = False
        self.node = self.nodes_dict[self.d_user]
        self.password = password
        self.started = 0
        self.add_event_handler("presence_subscribe", self.presence_subscribed)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("register", self.register)  # flag de register
        self.add_event_handler('message', self.message)
        # self.send_tables()

    @property
    def recipents(self):
        recipents_array = []
        for n in self.nodes_dict:
            if n != self.d_user:
                recipents_array.append(n)
        return recipents_array

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
        if msg['type'] in ('chat'):
            message_json = json.loads(msg["body"])
            if "to" in message_json:
                if message_json["to"] == self.d_user:
                    print("\n")
                    print("Se recibe mensaje de: ", message_json["from"])
                    print(message_json["message"], "\n")
                else:
                    print("Soy: ", self.boundjid.bare)
                    message_json["counter"] = message_json["counter"] - 1
                    if message_json["counter"] > 0:
                        for adyacent in self.node.adyacents:
                            print("Envaindo a : ", adyacent["node"])
                            to = self.node.compute_username(
                                adyacent["node"]).lower()
                            serialized_payload = json.dumps(message_json)
                            self.make_message(
                                mto=to,
                                mbody=serialized_payload,
                                mtype='chat',
                                mfrom=self.boundjid.bare
                            ).send()

            else:
                print("\n")
                print("Imprimamos", message_json["message"])

        elif msg["type"] == "normal":
            message_json = json.loads(msg["body"])
            type = message_json["type"]
            if type == "table":
                payload = message_json
                self.node.recieve_from_adyacent(payload)

            elif message_json["type"] == "update":
                print("Actualización de ruta: ")
                print(message_json["body"])
            else:
                print(message_json["body"])
        self.get_roster()

    def send_tables(self):
        all_valid = False

        while(not all_valid):
            all_valid_holder = True

            payload = self.node.create_destinations_payload()
            payload["type"] = "table"
            adyacents = self.node.adyacents
            for adyacent in adyacents:
                to = self.node.compute_username(adyacent["node"]).lower()
                serialized_payload = json.dumps(payload)
                self.make_message(mto=to,
                                  mbody=serialized_payload,
                                  mtype='normal',
                                  mfrom=self.boundjid.bare
                                  ).send()
                # self.recieve_messages()
                # await self.waiting_queue.join()
            all_valid = self.node.is_ready and all_valid_holder
            time.sleep(3)
            print(self.node.table)
            self.node.counter += 1

    def send_presence_subscriptions(self):
        for node in self.nodes_dict:
            self.send_presence_subscription(
                pto=self.node.compute_username(node), pfrom=self.user)

    async def start(self, event):
        self.inited = True
        self.send_presence()
        print("Conectado")
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
    def sendTableMessage(self, to, message):

        self.make_message(mto=to,
                          mbody=message,
                          mtype='normal',
                          mfrom=self.boundjid.bare
                          ).send()

    async def logOut(self):
        self.started = -1
        self.disconnect(wait=True)
