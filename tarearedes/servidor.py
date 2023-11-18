import socket
import threading
import json

# Cargar la lista de artefactos
with open('artefactos.json', 'r') as file:
    artifacts = json.load(file)

# Datos del servidor
host = 'localhost'
port = 12345

# Creamos el mutex
mutex = threading.Lock()

# Creación del socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Servidor corriendo en {host}:{port}")

# Guardado de datos
clients = []
usernames = []
artifacts_by_user = {}
trade_offers = {}

# Artefactos
def send_artifacts(client, username):
    if username in artifacts_by_user:
        user_artifacts_numbers = artifacts_by_user[username]
        user_artifacts_numbers = [artifacts[str(num)] for num in user_artifacts_numbers]

        artifacts_message = ', '.join(user_artifacts_numbers)
        message = f'[SERVER] Tus artefactos son: {artifacts_message}'
        client.send(message.encode('utf-8'))
    else:
        message = '[SERVER] No tienes artefactos.'
        client.send(message.encode('utf-8'))

# Reenvío de mensajes a los demás clientes
def broadcast(message, _client):
    for client in clients:
        if client != _client:
            client.send(message)

# Desconexión del cliente (eliminación de las listas y mensajes correspondientes)
def disconnected_client(client):
    index = clients.index(client)
    username = usernames[index]
    broadcast(f"[SERVER] {username} se ha desconectado.".encode('utf-8'), client)
    clients.remove(client)
    usernames.remove(username)
    client.close()
    print(f'{username} se ha desconectado.')

# Verificar si el nombre está disponible
def is_username_unique(username):
    return username not in usernames

# Mandar mensajes privados
def send_private_message(sender, recipient, message):
    try:
        recipient_client = clients[recipient]
        private_message = f'[Te ha susurrado] {sender} : {message}'
        recipient_client.send(private_message.encode('utf-8'))
    except ValueError:
        print('[SERVER] Usuario destinatario no encontrado.')

# Lista de usuarios
def get_connected_users():
    return ', '.join(usernames)

# Mandar info de los artefactos
def send_artefact_info(client, artifact_id):
    artifact_id = str(artifact_id)
    if artifact_id in artifacts:
        artifacts_name = artifacts[artifact_id]
        message = f'[SERVER] El artefacto {artifact_id} es {artifacts_name}'
    else:
        message = f'[SERVER] No se encontro el artefacto {artifact_id}'
    
    client.send(message.encode('utf-8'))

# Comprobar si posee los artefactos
def is_user_artifact(username, artifact_id):
    print("Usuario: ", username)
    print("Artefactos del usuario: ",artifacts_by_user[username])
    print("Artefacto ID:", artifact_id)
    print(type(artifact_id))
    print(type(artifacts_by_user))
    if int(artifact_id) in artifacts_by_user[username]:
        print("Entre al if")
        return True
    else:
        return False


# MODIFICAR
# Inicializar el trade
def initiate_trade(sender, recipient, my_artifact_id, their_artifact_id):
    with mutex:
        # Guardamos la oferta de intercambio
        trade_offers[sender] = {'recipient': recipient, 'my_artifact_id': my_artifact_id, 'their_artifact_id': their_artifact_id}
        offer_message = f'[SERVER] {sender} te ha ofrecido intercambiar {my_artifact_id} por {their_artifact_id}.'
        recipient.send(offer_message.encode('utf-8'))

# MODIFICAR
# Aceptar trade
def accept_trade(username):
    with mutex:
        if username in trade_offers:
            offer = trade_offers[username]
            sender = username
            recipient = offer['recipient']
            my_artifact_id = offer['my_artifact_id']
            their_artifact_id = offer['their_artifact_id']

            #Realizamos el intercambio
            artifacts_by_user[sender].remove(my_artifact_id)
            artifacts_by_user[sender].append(their_artifact_id)

            artifacts_by_user[recipient].remove(their_artifact_id)
            artifacts_by_user[recipient].append(my_artifact_id)

            # Mandamos un mensaje del intercambio aceptado
            message = '[SERVER] ¡Intercambio realizado!'
            clients[username].send(message.encode('utf-8'))
            clients[recipient].send(message.encode('utf-8'))

            # Borramos la oferta de intercambio
            del trade_offers[username]
            
# MODIFICAR
# Rechazar trade
def reject_trade(username):
    with mutex:
        if username in trade_offers:
            # Notificar al usuario que su oferta fue rechazada
            message = f'[SERVER] {username} ha rechazado tu oferta de intercambio.'
            clients[username].send(message.encode('utf-8'))

            # Limpiar la oferta de intercambio
            del trade_offers[username]

# Manejo de mensajes
def handle_message(client, username):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith(':'):
                commands_parts = message.split(' ')
                command = commands_parts[0]
                
                # ------------------ Comandos mínimos ------------------

                # Desconectarse del chat
                if command == ':q':
                    disconnected_client(client)
                    break

                # Mensaje privado
                elif command == ':p':
                    if(len(commands_parts) >= 3):
                        try: 
                            recipient_id = commands_parts[1]
                            recipient_username = usernames.index(recipient_id)
                            private_message = ' '.join(commands_parts[2:])
                            send_private_message(username, recipient_username, private_message)
                        except ValueError:
                            message = f'[SERVER] {recipient_id} no esta conectado.'
                            client.send(message.encode('utf-8'))
                    else:
                        message = '[SERVER] Formato incorrecto. Use: :p <Identificiador> <Mensaje>'
                        client.send(message.encode('utf-8'))

                # Lista de usuarios conectados
                elif command == ':u':
                    connected_users = get_connected_users()
                    message = f'[SERVER] Usuarios conectados: {connected_users}'
                    client.send(message.encode('utf-8'))

                # Enviar una carita feliz
                elif command == ':smile':
                    message = f'[SERVER] {username} envió: :)'
                    broadcast(message.encode('utf-8'), client)

                # Enviar una carita enojada
                elif command == ':angry':
                    message = f'[SERVER] {username} envió: >:('
                    broadcast(message.encode('utf-8'), client)

                # Enviar emoticón bélico 
                elif command == ':combito':
                    message = f'[SERVER] {username} envió: Q(’- ’Q)'
                    broadcast(message.encode('utf-8'), client)

                # Enviar una larva
                elif command == ':larva':
                    message = f'[SERVER] {username} envió: (:o)OOOooo'
                    broadcast(message.encode('utf-8'), client)

                # Lista de artefactos que el usuario tiene en su cuenta
                elif command == ':artefactos':
                    send_artifacts(client, username)

                # Identificador del artefacto
                elif command == ':artefacto':
                    artefact_id = int(commands_parts[1])
                    send_artefact_info(client, artefact_id)

                # Intercambio entre usuarios (DEBEN TENER MUTEX) # MODIFICAR
                elif command == ':offer':
                    if len(commands_parts) == 4:
                        try:
                            recipient_id = commands_parts[1]
                            recipient_username = usernames.index(recipient_id)
                            artifact_user = commands_parts[2]
                            artefact_recipient = commands_parts[3]
                            print("PASE EL LARGO")
                            print(recipient_id)
                            print(recipient_username)
                            # Verificar que sea un artefacto que poseen los usuarios
                            if is_user_artifact(username, artifact_user):
                                print("PASE EL PRIMER CHECK")
                                print(recipient_username)
                                if is_user_artifact(recipient_username, artefact_recipient):
                                    print("PASE EL SEGUNDO CHECK")
                                    initiate_trade(username, recipient_username, artifact_user, artefact_recipient)
                                else:
                                    message = f'[SERVER] {recipient_id} No posee el artefacto {artefact_recipient}'
                                    client.send(message.encode('utf-8'))
                            else:
                                message = f'[SERVER] No posees el artefacto {artifact_user}'
                                client.send(message.encode('utf-8'))
                        except ValueError:
                            message = f'[SERVER] {recipient_id} no esta conectado.'
                            client.send(message.encode('utf-8'))
                    else:
                        message = '[SERVER] Formato incorrecto. Use: :offer <Identificador> <MiArtefactoId> <SuArtefactoId>'
                        client.send(message.encode('utf-8'))

                # Aceptar intercambio # MODIFICAR
                elif command == ':accept':
                    accept_trade(username)

                # Rechazar intercambio # MODIFICAR
                elif command == ':reject':
                    reject_trade(username)
                
                # En caso de mandar un comando que no se conozca avisarle al usuario
                else:
                    message = '[SERVER] Comando no encontrado'
                    client.send(message.encode('utf-8'))

            else:
                broadcast(message.encode('utf-8'), client)
        except Exception as e:
            print(f"Error: {e}")
            disconnected_client(client)
            break

# Recibir conexiones
def receive_connection():
    while True:
        client, address = server.accept()

        username = client.recv(1024).decode('utf-8')

        if is_username_unique(username):
            clients.append(client)
            usernames.append(username)

            # Enviar el mensaje para que elija los artefactos
            message = f'Connected'
            client.send(message.encode('utf-8'))

            while True:
                # Recibir los artefactos del usuario
                chosen_artifacts = client.recv(1024).decode('utf-8').split(',')

                # Ver si hay strings vacios y pasarlos a int
                chosen_artifacts = [int(num) for num in chosen_artifacts if num]

                # Verificamos que sean a lo más 6 artefactos
                if len(chosen_artifacts) <= 6:

                    # Guardar los artefactos elegidos
                    artifacts_by_user[username] = chosen_artifacts

                    # Mandar los artefactos
                    send_artifacts(client, username)


                    # Mandar el mensaje de confirmación
                    client.send('[SERVER] ¿Está bien? (Sí/No)'.encode('utf-8'))

                    # Recibir la respuesta
                    confirmation_response = client.recv(1024).decode('utf-8')

                    if confirmation_response.lower() == 'si' or confirmation_response.lower() == 'sí' or confirmation_response.lower == 's':

                        # Mensaje de confirmación
                        message = '[SERVER] ¡OK!'
                        client.send(message.encode('utf-8'))

                        # Conexión de cliente
                        print(f'{username} conectado desde {str(address)}')
                        message = f'[SERVER] {username} se unió al chat!'.encode('utf-8')
                        broadcast(message, client)
                        client.send('Bienvenido al chat!'.encode('utf-8'))

                        thread = threading.Thread(target=handle_message, args=(client,username))
                        thread.start()

                        break
                    elif confirmation_response.lower() == 'no' or confirmation_response.lower() == 'n':
                        message = '[SERVER] Vuelve a elegir tus artefactos'
                        client.send(message.encode('utf-8'))
                    else:
                        print('[SERVER] Respuesta no válida. Por favor, eliga una opción')
                else:
                    print('[SERVER] Elija hasta 6 artefactos')
        else:
            client.send('El nombre de usuario ya está en uso. Por favor, elige otro.'.encode('utf-8'))

receive_connection()
