import socket
import comandos as co
import threading
import json
import re
import sys

from PyQt5 import QtGui, QtWidgets, uic, QtCore

with open('artefactos.json', 'r') as file:
    _artifacts = json.load(file)

# Protocolos internos de comunicacion cliente-servidor
p = ["msg", "cmd", "order"]

mtx = threading.Lock()
clientes = []

connection = True

# Mensaje de bienvenida
def bienvenida():
    print(r'''
                                           ,,                                                       ,,         ,,    ,,  
 .M"""bgd   mm                           `7MM                                 `7MM"""YMM            db       `7MM    db  
,MI    "Y   MM                             MM                                   MM    `7                       MM        
`MMb.     mmMMmm   ,6"Yb.  `7Mb,od8   ,M""bMM   .gP"Ya  `7M'    ,A    `MF'      MM   d   `7Mb,od8 `7MM    ,M""bMM  `7MM  
  `YMMNq.   MM    8)   MM    MM' "' ,AP    MM  ,M'   Yb   VA   ,VAA   ,V        MM""MM     MM' "'   MM  ,AP    MM    MM  
.     `MM   MM     ,pm9MM    MM     8MI    MM  8M""""""    VA ,V  VA ,V         MM   Y     MM       MM  8MI    MM    MM  
Mb     dM   MM    8M   MM    MM     `Mb    MM  YM.    ,     VVV    VVV          MM         MM       MM  `Mb    MM    MM  
P"Ybmmd"    `Mbmo `Moo9^Yo..JMML.    `Wbmd"MML. `Mbmmd'      W      W         .JMML.     .JMML.   .JMML. `Wbmd"MML..JMML.
''')

# Clase para el ingreso del nombre del granjero
class Client(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Iniciar con nombre
        self.login_ui = uic.loadUi('IngresarNombre.ui')
        self.login_ui.setWindowTitle('Ingreso Nombre')
        self.login_ui.pushButton.clicked.connect(self.check_name)
        self.login_ui.show()

        # Cliente
        self.chat_ui = uic.loadUi('ChatCliente.ui')
        self.chat_ui.setWindowTitle('Chat')
        self.chat_ui.pushButton.clicked.connect(self.send_message)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client_socket.connect(("127.0.0.1", 12345))
            bienvenida()
            self.acc_creation(self.client_socket)

            recibir_mensaje = threading.Thread(target=self.receive_messages, args=(self.client_socket,))
            send_thread = threading.Thread(target=self.send_messages, args=(self.client_socket, ))
            send_thread.daemon = True

            recibir_mensaje.start()
            send_thread.start()

            recibir_mensaje.join()
            send_thread.join()

        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            self.client_socket.close()

        

    def confirmar(self, name, client_socket):
        x = input(f"Confirmar nombre: {name} (Y/n)")
        if x == "" or x.lower() == "y":
            client_socket.send(f'{p[2]}\tname\t{name}'.encode('utf-8'))

            client_socket.settimeout(None)

            try:
                ACK = client_socket.recv(1024).decode('utf-8').strip().split("\t")
                protocol = ACK[0]

                if protocol == 'order':
                    subprotocol = ACK[1]
                    body = ACK[-1]

                    if subprotocol == 'ack':
                        if body == 'true':
                            print("CONECTANDO CON EL SERVIDOR")
                            return True
                        else:
                            print("Nombre ya existente. Pruebe con otro.")
                            return False

            except socket.timeout:
                print("Timeout: No se recibió respuesta del servidor.")
                return False

        return False

    
    def set_artifacts(self, artifacts, client_socket):
        user_artifacts = list(map(str, re.findall(r'\d+', artifacts)))
        print(f'Artefactos escogidos:')
        for a in user_artifacts:
            print(a, _artifacts[a])
        
        x = input(f"Confirmar artefactos? (Y/n)")

        if x == "" or x.lower() == "y":
            msg = f'order\tsave_artifact\t{artifacts}'.encode('utf-8')
            client_socket.send(msg)

            client_socket.settimeout(None)

            try:
                ACK = client_socket.recv(1024).decode('utf-8').strip().split("\t")
                protocol = ACK[0]

                if protocol == 'order':
                    subprotocol = ACK[1]
                    body = ACK[-1]

                    if subprotocol == 'ack':
                        if body == 'true':
                            print("[SERVER] ¡OK!")
                            print("¡Bienvenido/a al chat de Granjeros!")
                            return True
                        else:
                            print("[SERVER] Uno o más artefactos no existen.")
                            return False

            except socket.timeout:
                print("Timeout: No se recibió respuesta del servidor.")
                return False

        return False
    

    def acc_creation(self, client_socket):
        """creacion de personaje (SIN PASSWORD)"""
        while True:
            name = input("Antes de comenzar, cree un usuario "
                        "ingresando un nombre único:\n")

            print("\033[A\033[K", end='', flush=True)  # Move cursor up and clear the line

            if self.confirmar(name, client_socket):
                print(f"¡Conectado con el servidor {name}!")
                break

        while True:
            artifacts = input("[SERVER] Cuéntame, ¿Qué artefactos tienes?:\n" )

            print("\033[A\033[K", end='', flush=True)  # Move cursor up and clear the line

            if self.set_artifacts(artifacts, client_socket):
                break
            
    def receive_messages(self, client):
        global connection
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    print("Server closed the connection.")
                    break
                with mtx:
                    print(f"{message.decode('utf-8')}")
                
                if message.decode('utf-8') == '¡Adios y suerte completando tu colección!':
                    client.close()
                    break

                
            except Exception as e:
                print(e)
                break
        client.close()

    def send_messages(self, client):
        while True:
            message = input()
            print("\033[A\033[K", end='', flush=True)  # Move cursor up and clear the line
            try:
                if message[0].startswith(":"):
                    message = f'{p[1]}\t{message}'
                
                else:
                    # Se envia un mensaje normal
                    print("YO:", message)
                    message = f'{p[0]}\t{message}'

                client.send(message.encode('utf-8'))
            except Exception as e:
                print("AQUI OCURRO",e)
                client.close()
                break
            


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = Client()
    sys.exit(app.exec_())