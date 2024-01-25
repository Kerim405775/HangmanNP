import socket
import struct
import pickle
import random
import threading
from hangman_words import word_list
from hangman_art import logo, stages
from hangman_ranking import print_ranking, save_score

# Ustawienia multicastu
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 1234

# Ustawienia serwera TCP
TCP_IP = '0.0.0.0'
TCP_PORT = 12345
BUFFER_SIZE = 1024

# Tworzenie gniazda multicastowego
multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
multicast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
multicast_sock.bind(('', MULTICAST_PORT))

# Ustawienia TTL dla pakietów multicastowych
ttl = struct.pack('b', 1)
multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

# Dołączanie do grupy multicastowej
group = socket.inet_aton(MULTICAST_GROUP)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Funkcja do odbierania zapytań od klientów i wysyłania odpowiedzi
def multicast_response():
    while True:
        print("Czekam na zapytania od klientów...")
        data, addr = multicast_sock.recvfrom(1024)
        message = pickle.loads(data)
        if message['request'] == 'DISCOVER_SERVER':
            response = {'response': 'SERVER_HERE', 'tcp_port': TCP_PORT}
            multicast_sock.sendto(pickle.dumps(response), addr)
            print(f"Odpowiedziałem klientowi {addr} z informacją o serwerze.")

# Logika gry
def start_game(connection, client_address):
    connection.sendall(pickle.dumps(logo))
    chosen_word = random.choice(word_list)
    word_length = len(chosen_word)
    end_of_game = False
    lives = 6
    display = ['_'] * word_length
    guessed_letters = []

    while not end_of_game:
        game_state = f"{' '.join(display)}\n{stages[lives]}"
        prompt = "Guess a letter" if lives > 0 else "Game over"
        connection.sendall(pickle.dumps(f"{game_state}\n{prompt}"))

        if lives > 0:
            try:
                guess_data = connection.recv(BUFFER_SIZE)
                if not guess_data:
                    break  # Jeśli nie otrzymaliśmy danych, zakończ pętlę
                guess = pickle.loads(guess_data).lower()

                if len(guess) == 1 and guess.isalpha():
                    if guess in guessed_letters:
                        connection.sendall(pickle.dumps("You've already guessed this letter."))
                    else:
                        guessed_letters.append(guess)
                        if guess in chosen_word:
                            for position in range(word_length):
                                if chosen_word[position] == guess:
                                    display[position] = guess
                        else:
                            lives -= 1
                            if lives == 0:
                                end_of_game = True
                else:
                    connection.sendall(pickle.dumps("Please enter a single alphabetical letter."))
            except EOFError:
                # Klient nieoczekiwanie rozłączył się
                break
        else:
            end_of_game = True

        # Wyświetlanie stanu gry po stronie serwera
        print(f"Stan gry dla {client_address}: {' '.join(display)} - Pozostałe życia: {lives}")

    if end_of_game:
        result = "You win!" if "_" not in display else f"You lose.\nThe word was {chosen_word}."
        connection.sendall(pickle.dumps(result))
        print(f"Wynik gry dla {client_address}: {result}")

        # Zapisz wynik do rankingu i wyślij aktualny ranking do klienta
        player_name = str(client_address[1])  # Tutaj używamy adresu klienta jako nazwy, możesz to zmienić na coś bardziej unikalnego
        save_score(player_name, lives)
        ranking = print_ranking()
        send_ranking=""
        for name, score in ranking.items():
            send_ranking = send_ranking + f"{name}: {score}\n"
        connection.sendall(pickle.dumps(send_ranking))

    connection.close()  # Zamknij połączenie po zakończeniu gry
def update_ranking(client_address, lives):
    score = lives * 10  # Przykładowe obliczenie punktów
    with open("ranking.txt", "a") as ranking_file:
        ranking_file.write(f"{client_address[1]}: {score}\n") # Zamknij połączenie po zakończeniu gry


# Główna funkcja serwera
def server_main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((TCP_IP, TCP_PORT))
    server_sock.listen(5)
    print(f"TCP Server listening on {TCP_IP}:{TCP_PORT}")

    # Uruchomienie wątku obsługi multicastu
    threading.Thread(target=multicast_response, daemon=True).start()

    while True:
        conn, addr = server_sock.accept()
        print('Connection address:', addr)
        threading.Thread(target=start_game, args=(conn, addr)).start()

if __name__ == "__main__":
    server_main()
