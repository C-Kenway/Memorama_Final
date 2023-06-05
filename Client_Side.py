import socket

HOST = "localhost"
PORT = 12345
buffer_size = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    try:
        while True:
            response = client_socket.recv(buffer_size).decode().strip()
            print(response)
            if response == "Es tu turno":
                choice = input("Elige un índice de tarjeta para voltear: ")
                client_socket.send(choice.encode())
            elif response == "\n¡Felicidades! Ha ganado el juego\n":
                break
    finally:
        client_socket.close()
        print("Conexión cerrada")
