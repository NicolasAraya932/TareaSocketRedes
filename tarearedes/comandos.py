import xml.etree.ElementTree as ET
import threading

mtx = threading.Lock()

tree = ET.parse('comandos.xml')

root = tree.getroot()

# Muestra en pantalla lista de comandos
def help(client_socket):
    with open("comandos.txt", mode='r', encoding='utf-8') as f:
        for line in f:
            client_socket.send(line.encode('utf-8'))

# Desconexión del cliente (eliminación de las listas y mensajes correspondientes)
def disconnected_client(client, clients):
    broadcast(f"[SERVER] {clients[client].nombre} se ha desconectado.".encode('utf-8'), clients[client].nombre, clients)
    print(f'{clients[client].nombre} se ha desconectado.')

# Mandar mensajes privados
def send_private_message(sender, recipient_socket, message):
    try:
        private_message = f'[{sender} te ha susurrado] {message}'
        recipient_socket.send(private_message.encode('utf-8'))
    except ValueError:
        print('[SERVER] Usuario destinatario no encontrado.')

# Envio de mensajes a los demás clientes
def broadcast(message, _client, clients):
    for client in clients.values():
        if client.nombre != _client:
            client.client_socket.send(message)

# Mostrar artefactos del usuario
def show_artifacts(current_user):
    current_user.client_socket.send(f'[SERVER] Tus artefactos son:'.encode('utf-8'))
    for key, artifact in current_user.artefactos.items():
        current_user.client_socket.send(f'---- {key} {artifact}\n'.encode('utf-8'))

# Mostrar artefacto solicitado por ID
def get_artifact(artefact_id, artifacts, current_user):
    try:
        print(artifacts[artefact_id], current_user)
        current_user.client_socket.send(f'[SERVER] El artefacto {artefact_id} es {artifacts[artefact_id]}'.encode('utf-8'))
    except:
        current_user.client_socket.send(f'[SERVER] El artefacto {artefact_id} no existe.'.encode('utf-8'))