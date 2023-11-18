import socket
import threading
import sys

host = 'localhost'
port = 8080

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))


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
bienvenida()
username = input("Ingrese su nombre de usuario: ")

def receive_messages():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except:
            print("Error receiving messages.")
            client.close()
            break

def send_messages():
    while True:
        message = input()
        if message.startswith(':'):
            client.send(message.encode('utf-8'))
            if message == ':q':
                print('¡Adiós y suerte completando tu colección! \nDesconectando del servidor...')
                client.close()
                break
            
        else:       
            message = f'{username} : {message}'
            client.send(message.encode('utf-8'))

def main():
    try:
        client.send(username.encode('utf-8'))

        response = client.recv(1024).decode('utf-8')

        if 'Connected' in response:
            print(f"Conectado con el servidor, {username}!")

            while True:
                # Seleccionar los primeros 6 artefactos
                user_input = input("[SERVER] Ingresa los números de tus primeros 6 artefactos separados por comas (1-42):\n")
                client.send(user_input.encode('utf-8'))

                # Recibir el mensajes de los artefactos seleccionados
                artifacts_message = client.recv(1024).decode('utf-8')
                print(artifacts_message)

                # Recibir el mensaje de confirmación
                confirmation_message = client.recv(1024).decode('utf-8')
                print(confirmation_message)

                if '[SERVER] ¿Está bien? (Sí/No)' in confirmation_message:
                    # Preguntar al usuario si los artefactos son correctos
                    confirmation_response = input().lower()
                    client.send(confirmation_response.encode('utf-8'))

                    if confirmation_response == 'sí' or confirmation_response == 'si' or confirmation_response == 's':
                        last_message = client.recv(1024).decode('utf-8')
                        print(last_message)
                        receive_thread = threading.Thread(target=receive_messages)
                        receive_thread.start()

                        send_thread = threading.Thread(target=send_messages)
                        send_thread.start()

                        break
                    elif confirmation_response == 'no' or confirmation_response == 'n':
                        last_message = client.recv(1024).decode('utf-8')
                        print(last_message)
                else:
                    print("[SERVER] Confirmación no recibida. Cerrando la conexión.")
        elif 'El nombre de usuario ya está en uso. Por favor, elige otro.' in response:
            print(f'El nombre de usuario {username} ya está en uso.')

    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':

    bienvenida() 
    main()