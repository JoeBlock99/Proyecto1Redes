from clientxmpp import Client
from constants import XMPP_DOMAIN, XMPP_TIMEOUT
from helpers import index_of_list, required_input
import json
from time import sleep
from threading import Thread
from dijstra import calcPath, calcRoutes, nextNode


def xmpp_thread(xmpp, computed_stop):
    try:
        xmpp.process(forever=False, timeout=XMPP_TIMEOUT)
    except:
        print("Solo perdidas")
        xmpp.disconnect()


if __name__ == '__main__':
    # Setup logging.
    # logging.basicConfig(level=logging.INFO,
    #                     format='%(levelname)-8s %(message)s')
    options = ["Registrarse", "Login", "Salir"]
    option = index_of_list(options)
    if(option == 0):
        user = required_input("Username: ")
        password = required_input("Password: ")
        xmpp = Client(user+"@" + XMPP_DOMAIN, password)
        xmpp.register_plugin('xep_0004')  # Data forms
        xmpp.register_plugin('xep_0066')  # Out-of-band Data
        xmpp.register_plugin('xep_0077')
        xmpp.register_plugin('xep_0085')
        xmpp['xep_0077'].force_registration = True
        xmpp.connect()
    elif(option == 1):
        user = required_input("Username: ")
        password = required_input("Password: ")
        xmpp = Client(user+"@" + XMPP_DOMAIN, password)
        xmpp.register_plugin('xep_0030')  # Service Discovery
        xmpp.register_plugin('xep_0199')  # XMPP Ping
        xmpp.register_plugin('xep_0092')
        xmpp.register_plugin('xep_0363')
        xmpp.register_plugin('xep_0085')
        xmpp.connect()

    tt = Thread(
        target=xmpp_thread, args=(xmpp, lambda: xmpp.started == -1))
    tt.start()
    print("Esperando respuesta del servidor...")
    sleep(XMPP_TIMEOUT)
    if(not xmpp.inited or xmpp.started == -1):
        print("No se pudo conectar al server")
        xmpp.disconnect(wait=True)
        exit(0)
    _ = input("Presione enter para empezar a calcular tablas: \n")
    print("las tablas obtenidas fueron las siguientes:\n", calcRoutes(user))
    options = ["Mandar mensaje", "Salir"]
    showMenu = True
    while(showMenu):
        menu = index_of_list(options)
        if(menu == 0):
            recipent = xmpp.get_recipent()
            message = required_input("Message: ")
            message_json = {
                "message": message,
                "to": recipent,
                "from": xmpp.d_user
            }
            destinatary = nextNode(user, recipent)
            print("Enviando mensaje a ", destinatary)
            destinatary = xmpp.compute_username(destinatary)

            xmpp.make_message(mto=destinatary,
                              mbody=json.dumps(message_json),
                              mtype='chat').send()
        else:
            xmpp.logOut()
            showMenu = False


exit(0)
