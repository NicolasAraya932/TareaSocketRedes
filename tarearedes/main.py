import socket
from clientes import Cliente
import threading
import comandos as cmd
import re

import json

# MUTEX
clientes_t = threading.Lock()


# Se guarda en diccionario clave: socket y body: clase cliente.
clientes = dict()

# Se guarda en trade_system cada tradeo con clave: nombre destino y cuerpo informacion de tradeo.
trade_system = dict()

# Protocolos internos comunicacion cliente-servidor
p = ["msg", "cmd", "order"]

"""_summary_ order
El servidor se encargara de atender los siguientes protocolos:

"msg": Corresponde a un mensaje hacia el servidor
"cmd": Corresponde a un comando que el cliente quiere realizar
"order": Especial para comunicación con servidor y viceversa
"""
with open('artefactos.json', 'r') as file:
    artifacts = json.load(file)

#---------- SAVE USER ---------- 
def save_name(client_socket, name):
    """Guardado del nombre del cliente en la lista de clientes"""
    global clientes, clientes_t
    with clientes_t:
        if any(cliente.nombre == name for cliente in clientes.values()):
            ACK = f'order\tack\tfalse'.encode('utf-8')
            client_socket.send(ACK)
        else:
            ACK = f'order\tack\ttrue'.encode('utf-8')
            client_socket.send(ACK)

            current_c = Cliente(str(client_socket.getpeername()), name, client_socket=client_socket)
            clientes[client_socket] = current_c
            print(f'Usuario creado con exito!, nombre: {name} , instancia: {current_c}')

#---------- SAVE ARTIFACTS ---------
def save_artifact(client_socket, user_artifacts):
    global clientes, clientes_t
    with clientes_t:
        user_artifacts = list(map(str, re.findall(r'\d+', user_artifacts)))
        if len(user_artifacts) <= 6:
            try:
                for a in user_artifacts:
                    clientes[client_socket].artefactos[a] = artifacts[a]
                ACK = f'order\tack\ttrue'.encode('utf-8')
                client_socket.send(ACK)
                print(f"Artefactos de {clientes[client_socket].nombre} guardados con exito!")
                print(f"Usuario: {clientes[client_socket].nombre}, Artefactos :{clientes[client_socket].artefactos}")

                cmd.broadcast(f"[SERVER] {clientes[client_socket].nombre} se ha conectado.".encode('utf-8'), clientes[client_socket].nombre, clientes)
            except:
                ACK = f'order\tack\tfalse'.encode('utf-8')
                client_socket.send(ACK)


# ORDER PROTOCOL
order = {'name': lambda arg, _arg: save_name(arg, _arg),
         'ack': lambda arg, _arg: None,
         'save_artifact': lambda arg, _arg: save_artifact(arg, _arg)}

def handle_client(client_socket):
    global clientes, clientes_t
    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        mensaje = data.decode('utf-8').strip().split("\t")
        protocol = mensaje[0]
        subprotocol = mensaje[1]
        body = mensaje[-1]

        if protocol == 'order':

            # ORDER PROTOCOL
            order[subprotocol](client_socket, body)

        elif protocol == 'msg':
            # Broadcast para envío de mensajes
                ms = f'{clientes[client_socket].nombre}: {body}'.encode('utf-8')
                cmd.broadcast(ms, clientes[client_socket].nombre, clientes)

        elif protocol == 'cmd':
            # ------------------ Comandos mínimos ------------------

            # Separar mensaje en partes
            commands_parts = body.strip().split(" ")

            # Adquirir el comando especifico
            body = commands_parts[0]

            # Sacamos el cliente actual
            current_user = clientes[client_socket]
            print(f'Cliente: {current_user.nombre}, Comandos: {commands_parts}')
            
            # Nuevo comando, para mostrar comandos disponibles
            if body == ':?' or body == ':h' or body == ':help':
                cmd.help(client_socket)
            # Desconectarse del chat
            elif body == ':q':
                client_socket.send("¡Adios y suerte completando tu colección!".encode('utf-8'))
                cmd.disconnected_client(client_socket, clientes)
                clientes.pop(client_socket)
                break

            # Mensaje privado 
            elif body == ':p':
                if(len(commands_parts) >= 3):
                    try: 
                        # Adquirir comando
                        recipient_id = commands_parts[1]
                        # Guardar el mensaje
                        private_message = ' '.join(commands_parts[2:])

                        # Verificamos si se encuentra algún comenado especial
                        if ':smile' in private_message:
                            private_message =  private_message.replace(':smile', ':)')
                        elif ':angry' in private_message:
                            private_message =  private_message.replace(':angry', '>:(')
                        elif ':combito' in private_message:
                            private_message =  private_message.replace(':combito', 'Q(’- ’Q)')
                        elif ':larva' in private_message:
                            private_message =  private_message.replace(':larva', '(:o)OOOooo')
                        # Mandar el mensaje
                        client_socket.send(f"[Yo -> {recipient_id}] {private_message}".encode('utf-8'))

                        # Busqueda de socket por nombre
                        dest_socket = next((cliente.client_socket for cliente in clientes.values() if cliente.nombre == recipient_id), None)

                        if dest_socket:
                            cmd.send_private_message(current_user.nombre, dest_socket, private_message)
                        else:
                            client_socket.send(f'[SERVER] {recipient_id} no esta conectado.'.encode('utf-8'))
                    except Exception as e:
                        message = f'[SERVER] {e}'
                        client_socket.send(message.encode('utf-8'))
                else:
                    message = '[SERVER] Formato incorrecto. Use: :p <Identificiador> <Mensaje>'
                    client_socket.send(message.encode('utf-8'))

            # Lista de usuarios conectados
            elif body == ':u':
                connected_users = list(map(lambda x:x.nombre, clientes.values()))
                message = f'[SERVER] Usuarios conectados: {connected_users}'
                client_socket.send(message.encode('utf-8'))

            # Enviar una carita feliz
            elif body == ':smile':
                client_socket.send(f'[SERVER] Yo: :)'.encode('utf-8'))
                message = f'[SERVER] {current_user.nombre} envió: :)'
                cmd.broadcast(message.encode('utf-8'), current_user.nombre, clientes)

            # Enviar una carita enojada
            elif body == ':angry':
                client_socket.send(f'[SERVER] Yo: >:('.encode('utf-8'))
                message = f'[SERVER] {current_user.nombre} envió: >:('
                cmd.broadcast(message.encode('utf-8'), current_user.nombre, clientes)

            # Enviar emoticón bélico 
            elif body == ':combito':
                client_socket.send(f'[SERVER] Yo: Q(’- ’Q)'.encode('utf-8'))
                message = f'[SERVER] {current_user.nombre} envió: Q(’- ’Q)'
                cmd.broadcast(message.encode('utf-8'), current_user.nombre, clientes)

            # Enviar una larva
            elif body == ':larva':
                client_socket.send(f'[SERVER] Yo: (:o)OOOooo'.encode('utf-8'))
                message = f'[SERVER] {current_user.nombre} envió: (:o)OOOooo'
                cmd.broadcast(message.encode('utf-8'), current_user.nombre, clientes)

            # Lista de artefactos que el usuario tiene en su cuenta
            elif body == ':artefactos':
                cmd.show_artifacts(current_user)

            # Identificador del artefacto
            elif body == ':artefacto':
                artefact_id = commands_parts[1]
                cmd.get_artifact(artefact_id, artifacts, current_user)

            # Ofrecer intercambio
            elif body == ':offer':
                # Verificar que se cumpla el formato requerido
                if len(commands_parts) == 4:
                    
                    # Sacamos las partes del comando
                    identificador = commands_parts[1]
                    miartefactoid = commands_parts[2]
                    suartefactoid = commands_parts[3]
                    dest_socket = next((cliente.client_socket for cliente in clientes.values() if cliente.nombre == identificador), None)

                    if dest_socket:
                        # Comprobamos que esten los items en su inventario
                        A = any(key == miartefactoid for key, artefacto in current_user.artefactos.items())
                        B = any(key == suartefactoid for key, artefacto in clientes[dest_socket].artefactos.items())
                        if A and B:
                            with clientes_t:
                                trade_system[identificador] = [current_user.client_socket, dest_socket, miartefactoid, suartefactoid]
                                print(f'Se ha iniciado un intercambio entre {current_user.nombre} y {clientes[dest_socket].nombre}, objetos a intercambiar: {artifacts[miartefactoid]} (ID: {miartefactoid}), {artifacts[suartefactoid]} (ID: {suartefactoid})')
                                offer_msg = f'[SERVER] {current_user.nombre} te ha enviado una oferta: Te ofrece su {artifacts[miartefactoid]} (ID: {miartefactoid}) por tu {artifacts[suartefactoid]} (ID: {suartefactoid})\n(:accept, :reject) or ignore.'
                                current_user.client_socket.send(f'[SERVER] Has enviado una oferta a {clientes[dest_socket].nombre}: Ofreces tu {artifacts[miartefactoid]} (ID: {miartefactoid}) por su {artifacts[suartefactoid]} (ID: {suartefactoid})'.encode('utf-8'))
                                dest_socket.send(offer_msg.encode('utf-8'))
                        # Mensaje de que no estan los items en su inventario
                        else:
                            if not A:
                                current_user.client_socket.send(f'[SERVER] El artefacto {artifacts[miartefactoid]} (ID: {miartefactoid}) no se encuentra en tu inventario.'.encode('utf-8'))
                            if not B:
                                current_user.client_socket.send(f'[SERVER] El artefacto {artifacts[suartefactoid]} (ID: {suartefactoid}) no se encuentra en su inventario.'.encode('utf-8'))
                    else:
                        message = f'[SERVER] El usuario {identificador} no se encuentra conectado.'
                        client_socket.send(message.encode('utf-8'))
                else:
                    message = '[SERVER] Formato incorrecto. Use: :offer <Identificador> <MiArtefactoId> <SuArtefactoId>'
                    client_socket.send(message.encode('utf-8'))
 
            # Aceptar intercambio 
            elif body == ':accept':
                try:
                    with clientes_t:
                        sender, receiver, sender_artifact, receiver_artifact= trade_system[current_user.nombre]

                        # Realizacion de intercambio y eliminacion de artefactos
                        clientes[sender].artefactos[receiver_artifact] = artifacts[receiver_artifact]
                        clientes[receiver].artefactos[sender_artifact] = artifacts[sender_artifact]

                        clientes[sender].artefactos.pop(sender_artifact) 
                        clientes[receiver].artefactos.pop(receiver_artifact) 

                        # Mandar mensaje a los usuarios
                        sender.send(f'[SERVER] ¡Intercambio realizado con {clientes[receiver].nombre}!'.encode('utf-8'))
                        receiver.send(f'[SERVER] ¡Intercambio realizado con {clientes[sender].nombre}!'.encode('utf-8'))
                        print(f'Intercambio realizado con éxito entre {clientes[receiver].nombre} y {clientes[sender].nombre}')
                        trade_system.pop(current_user.nombre)

                except:
                    current_user.client_socket.send(f'[SERVER] No hay ofertas disponibles.'.encode('utf-8'))

           # Rechazar intercambio 
            elif body == ':reject':
                try:
                    with clientes_t:
                        sender, receiver, sender_artifact, receiver_artifact= trade_system[current_user.nombre]
                        trade_system.pop(current_user.nombre)

                        # Mandar mensaje a los usuarios
                        sender.send(f'[SERVER] {clientes[receiver].nombre} ha rechazado la oferta.'.encode('utf-8'))
                        receiver.send(f'[SERVER] Has rechazado la oferta de {clientes[sender].nombre}.'.encode('utf-8'))
                        print(f'Intercambio rechazado por {clientes[receiver].nombre}')

                except:
                    current_user.client_socket.send(f'[SERVER] No hay ofertas disponibles'.encode('utf-8'))
            
            # En caso de mandar un comando que no se conozca avisarle al usuario
            else:
                message = '[SERVER] Comando no encontrado. ":? o :h o :help" para lista de comandos'
                client_socket.send(message.encode('utf-8'))

    client_socket.close()


def main():
    # Inicialización del servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(("127.0.0.1", 12345))
        server_socket.listen()

        print("El servidor ha iniciado. Esperando conexiones...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Conexión aceptada desde {client_address}")
            cliente_thread = threading.Thread(target=handle_client, args=(client_socket, ))
            cliente_thread.start()

    except Exception as e:
        print(e)
    finally:
        server_socket.close()


if __name__=='__main__':
    main()
