import sys

if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input


def print_list(list):
    for i, item in enumerate(list):
        print(i+1, ") ", str(item))


def required_input(text="Ingrese "):
    while True:
        i = raw_input(text)
        if i != "":
            return i
        print("Es un campo obligatorio")


def int_input(input_message):
    while True:
        i = raw_input(input_message)
        try:
            return int(i)
        except:
            print("Ingrese un valor numerico")


def index_of_list(list, input_message="Seleccione una opción: ", error_message="Ingrese una opción valida"):
    while True:
        print_list(list)
        index = int_input(input_message)
        if index > 0 and index <= len(list):
            return index - 1
        else:
            print(error_message)
