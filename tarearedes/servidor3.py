import socket
import threading

# Crear un socket del servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("127.0.0.1", 12345))
server_socket.listen(5)

# Lista para mantener un registro de todos los clientes conectados
clientes = []

# Función para manejar la conexión de un cliente
def manejar_cliente(client_socket, addr):
    with client_socket:
        print(f"Conexión establecida desde {addr}")
        clientes.append(client_socket)
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            mensaje = data.decode()
            print(f"Cliente {addr}: {mensaje}")
            # Reenviar el mensaje a todos los clientes
            for cliente in clientes:
                if cliente != client_socket:
                    cliente.send(data)
        print(f"Cliente {addr} desconectado.")
        clientes.remove(client_socket)

# Escuchar y aceptar conexiones de clientes
while True:
    client_socket, client_addr = server_socket.accept()
    cliente_thread = threading.Thread(target=manejar_cliente, args=(client_socket, client_addr))
    cliente_thread.start()