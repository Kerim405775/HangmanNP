import socket
import pickle
import struct

# Ustawienia multicastu
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 1234
BUFFER_SIZE = 1024


# Funkcja do wyszukiwania serwera za pomocą multicastu
def find_server():
    multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    multicast_sock.settimeout(2)

    # Dołączanie do grupy multicastowej
    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    try:
        # Wysyłanie zapytania o serwer
        message = {'request': 'DISCOVER_SERVER'}
        multicast_sock.sendto(pickle.dumps(message), (MULTICAST_GROUP, MULTICAST_PORT))
        data, _ = multicast_sock.recvfrom(BUFFER_SIZE)
        response = pickle.loads(data)
        return response['tcp_port']
    except socket.timeout:
        print("Nie znaleziono serwera.")
        return None


# Funkcja do łączenia się z serwerem i rozpoczęcia gry
def start_game(tcp_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('localhost', tcp_port))
        while True:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("No data received from the server. Exiting.")
                break
            message = pickle.loads(data)
            print(message)

            if "Guess a letter" in message:
                while True:  # Pętla do walidacji wprowadzonej litery
                    guess = input("Twoja litera: ").lower()
                    if len(guess) == 1 and guess.isalpha():  # Sprawdzenie czy wprowadzony znak to jedna litera
                        print(f"Wysyłam literę {guess} do serwera...")
                        sock.sendall(pickle.dumps(guess))
                        break  # Wyjście z pętli walidacji po poprawnym wprowadzeniu
                    else:
                        print("Please enter a single alphabetical letter.")  # Komunikat o błędzie


if __name__ == "__main__":
    print("Szukam serwera...")
    server_port = find_server()
    if server_port:
        print(f"Znaleziono serwer. Łączę się na porcie {server_port}...")
        start_game(server_port)
    else:
        print("Nie można połączyć się z serwerem.")
