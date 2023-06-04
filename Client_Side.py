import socket

HOST = "localhost"
PORT = 12345
buffer_size = 1024

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

cliente.connect((HOST, PORT))
print('Se ha establecido una conexión con el servidor remoto.')

while True:
    respuesta = cliente.recv(buffer_size).decode()  # Espera la señal de que es su turno
    if "Es tu turno" in respuesta:
        seleccion = int(input('\nIngrese el número de la carta que desea voltear (0-7): '))
        cliente.send(str(seleccion).encode())
        carta_volteada = cliente.recv(buffer_size).decode()
        print(carta_volteada)
        respuesta = cliente.recv(buffer_size).decode()
        print(f"Respuesta del servidor:{respuesta}")
        if '\n¡Felicidades! Ha ganado el juego' in respuesta:
            break

cliente.close()
