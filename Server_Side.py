import socket
import random
import threading
from queue import Queue
from threading import Barrier, Semaphore

HOST = "localhost"
PORT = 12345
buffer_size = 1024
numConn = 3

game_state = None
lock = threading.Lock()
board = None
clients = []  # Una lista de clientes para mantener el orden de los turnos

start_barrier = Barrier(numConn)  # Barrier para sincronizar el inicio del juego
turn_semaphore = Semaphore(0)  # Semáforo para controlar los turnos de los jugadores

class BoardManager:
    def __init__(self, board, flipped_cards):
        self.board = board
        self.flipped_cards = flipped_cards
        self.lock = threading.Lock()

    def get_board(self):
        return self.board

    def get_flipped_cards(self):
        with self.lock:
            return self.flipped_cards[:]

    def flip_card(self, index, card):
        with self.lock:
            self.flipped_cards[index] = card

def build_board(difficulty):
    if difficulty == 1:
        words = ['gato', 'perro', 'oso', 'conejo']
        board_size = 8
    elif difficulty == 2:
        words = ['gato', 'perro', 'oso', 'conejo', 'pez', 'lobo', 'jirafa', 'canario', 'iguana']
        board_size = 18
    else:
        return 'Opción inválida', None, None

    return f"Modo: {'Principiante' if difficulty == 1 else 'Avanzado'}", random.sample(words * 2, board_size), ['X'] * board_size

def play_game(client_socket, board_manager):
    global clients, turn_semaphore
    board = board_manager.get_board()
    attempts = 0
    last_choice = None
    carta_previa = None

    while True:
        turn_semaphore.acquire()  # Adquirir el semáforo para obtener el turno

        # Actualizar el cliente actual al cliente en la parte delantera de la lista
        current_client = clients[0]
        # Rotar la lista de clientes para que el próximo cliente esté al frente
        clients = clients[1:] + clients[:1]

        if current_client != client_socket:
            turn_semaphore.release()  # Liberar el semáforo si no es el turno del cliente actual
            continue

        client_socket.send(str("Es tu turno").encode())

        choice = int(client_socket.recv(buffer_size).decode().strip())
        flipped_cards = board_manager.get_flipped_cards()

        if choice < 0 or choice >= len(flipped_cards):
            client_socket.send(str('Intente de nuevo.').encode())
            client_socket.send(str('Opción inválida').encode())
            attempts = 0
        elif flipped_cards[choice] != 'X':
            client_socket.send(str("Anterior:" + carta_previa).encode())
            client_socket.send(str('Carta ya seleccionada').encode())
            attempts = 0
        else:
            attempts += 1
            carta = board[choice]
            board_manager.flip_card(choice, carta)
            if attempts == 2:
                client_socket.send(str(carta).encode())
                if last_choice is not None and board[choice] == board[last_choice]:
                    client_socket.send(str('\n¡Felicidades! Ha formado una pareja').encode())
                    board_manager.flip_card(last_choice, board[last_choice])
                    board_manager.flip_card(choice, board[choice])
                    attempts = 0
                    if "X" not in board_manager.get_flipped_cards():
                        client_socket.sendall(str('\n¡Felicidades! Ha ganado el juego\n').encode())
                        turn_semaphore.release()  # Liberar el semáforo antes de finalizar el juego
                        break
                else:
                    client_socket.sendall(str('No fue pareja. Sigue jugando\n').encode())
                    if last_choice is not None:
                        board_manager.flip_card(last_choice, 'X')
                    board_manager.flip_card(choice, 'X')
                    attempts = 0
            elif attempts == 1:
                client_socket.sendall(str(carta).encode())
                client_socket.sendall(str('Siguiente tiro').encode())
                last_choice = choice
                carta_previa = carta

        turn_semaphore.release()  # Liberar el semáforo al finalizar el turno


# En la función run_game, en lugar de poner al cliente en la cola,
# lo añadimos a la lista de clientes.
def run_game(client_socket, game_state):
    global board, clients, turn_semaphore
    message, game_board, flipped_cards = game_state

    if game_board is None:
        client_socket.send(message.encode())
        client_socket.close()
        return

    with lock:
        if board is None:
            board = game_board

    board_manager = BoardManager(board, flipped_cards)

    clients.append(client_socket)  # Añadimos el cliente a la lista de clientes en lugar de la cola

    start_barrier.wait()  # Esperar a que todos los clientes estén listos

    # Desbloqueamos el semáforo una vez que todos los clientes están listos
    if clients[0] == client_socket:
        turn_semaphore.release()

    play_game(client_socket, board_manager)
    client_socket.close()
def servirPorSiempre(socketTcp, listaconexiones):
    global game_state
    difficulty = int(input("\nDificultad: 1)Principiante 2)Avanzado \n Ingrese numero:\n"))
    try:
        while True:
            client_conn, client_addr = socketTcp.accept()
            print("Conexión establecida con", client_addr)
            listaconexiones.append(client_conn)
            if game_state is None:
                game_state = build_board(difficulty)
            threading.Thread(target=run_game, args=(client_conn,game_state)).start()
            gestion_conexiones(listaconexiones)
    finally:
        for conn in listaconexiones:
            conn.close()

def gestion_conexiones(listaconexiones):
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)

listaconexiones = []
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socketTcp:
    socketTcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socketTcp.bind((HOST, PORT))
    socketTcp.listen(numConn)
    print("Esperando conexiones en el puerto", PORT)
    servirPorSiempre(socketTcp, listaconexiones)
