import socket
import pickle
import struct

# Multicast group information
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 1234

# Client
class MulticastClient:
    def __init__(self, client_id):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(5)
        self.client_id = client_id

    def start(self):
        self.join_group()

        while True:


            message = input("Enter a message: ")
            if message.lower() == 'exit':
                break

            # Send a message to the server
            self.send({"client_id": self.client_id, "message": message})

            # Receive and display the acknowledgment from the server
            response = self.receive()
            print(response)
            # if response is not None:
            #     print(f"Received from server: {response}")

    def join_group(self):
        group = socket.inet_aton(MULTICAST_GROUP)
        self.client_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack('4sL', group, socket.INADDR_ANY))

    def receive(self):
        try:
            data, _ = self.client_socket.recvfrom(1024)
            message = pickle.loads(data)
            return message

        except socket.timeout:
            print("TimeoutError: No data received from the server.")
            return None

    def send(self, message):
        data = pickle.dumps(message)
        self.client_socket.sendto(data, (MULTICAST_GROUP, MULTICAST_PORT))

if __name__ == "__main__":
    client_id = input("Enter client ID: ")
    client = MulticastClient(client_id)
    client.start()

