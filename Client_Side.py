import socket

HOST = "localhost"
PORT = 12345
buffer_size = 1024

def play_game(s):
    while True:
        # Recibir y decodificar los datos
        data = s.recv(buffer_size).decode()

        # Verificar si los datos no están vacíos
        if not data:
            print("Juego terminado.")
            break

        # Imprimir el mensaje del servidor
        print(data)

        # Verificar si es el turno del cliente para jugar
        if "Es tu turno" in data:
            # Solicitar al usuario que ingrese su elección y enviarla al servidor
            choice = input("Ingresa el número de la tarjeta que deseas voltear: ")
            s.send(choice.encode())
    s.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Conectarse al servidor
    s.connect((HOST, PORT))

    # Iniciar el juego
    play_game(s)
