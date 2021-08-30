from clientxmpp import Client
from constants import XMPP_DOMAIN
from node import Node, build_prod_nodes
from helpers import index_of_list, required_input
import logging
import sys
import json
import asyncio
from threading import Thread


def xmpp_thread(xmpp, computed_stop):
    try:
        xmpp.process(forever=True)
    except:
        print("Solo perdidas")
        xmpp.disconnect()


if __name__ == '__main__':
    # Setup logging.
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(levelname)-8s %(message)s')
    options = ["Resgistrarse", "Login", "Salir"]
    _nodes = build_prod_nodes()
    nodes_dict = {}
    for node in _nodes:
        nodes_dict[node.name] = node
    option = index_of_list(options)
    if(option == 0):
        user = required_input("Username: ")
        password = required_input("Password: ")
        xmpp = Client(user+"@" + XMPP_DOMAIN, password, nodes_dict)
        xmpp.register_plugin('xep_0004')  # Data forms
        xmpp.register_plugin('xep_0066')  # Out-of-band Data
        xmpp.register_plugin('xep_0077')
        xmpp.register_plugin('xep_0085')
        xmpp['xep_0077'].force_registration = True
        xmpp.connect()
    elif(option == 1):
        user = required_input("Username: ")
        password = required_input("Password: ")
        xmpp = Client(user+"@" + XMPP_DOMAIN, password, nodes_dict)
        xmpp.register_plugin('xep_0030')  # Service Discovery
        xmpp.register_plugin('xep_0199')  # XMPP Ping
        xmpp.register_plugin('xep_0092')
        xmpp.register_plugin('xep_0363')
        xmpp.register_plugin('xep_0085')
        xmpp.connect()

    tt = Thread(
        target=xmpp_thread, args=(xmpp, lambda: xmpp.started == -1))
    tt.start()
    _ = input("Presione cualquier tecla para empezar a calcular tablas: \n")
    xmpp.send_tables()
    xmpp.send_presence_subscriptions()
    options = ["Mandar mensaje", "Salir"]
    showMenu = True
    while(showMenu):
        menu = index_of_list(options)
        if(menu == 0):
            recipent = xmpp.get_recipent()
            to = xmpp.node.compute_username(recipent).lower()
            message = required_input("Message: ")
            message_json = {
                "message": message,
                "to": recipent,
                "from": xmpp.d_user
            }
            destinatary = xmpp.node.get_next_node(recipent)
            print("Enviando mensaje a ", destinatary)
            if destinatary is None:
                destinatary = to
            else:
                destinatary = xmpp.node.compute_username(destinatary)

            xmpp.make_message(mto=destinatary,
                              mbody=json.dumps(message_json),
                              mtype='chat').send()
        else:
            xmpp.logOut()
            showMenu = False


sys.exit(0)
