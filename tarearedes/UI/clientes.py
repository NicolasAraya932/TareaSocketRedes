import socket

class Cliente():

    def __init__(self, _id,  nombre, client_socket, artefactos=None):

        self.id = _id
        self.nombre = nombre
        self.client_socket = client_socket
        self.artefactos = artefactos or {}