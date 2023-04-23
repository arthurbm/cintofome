import socket
import time
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB
from packet import Packet
import random

filename = "example.txt"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define um tempo limite para receber uma resposta do servidor (em segundos)
sock.settimeout(TIMEOUT_LIMIT)

seq_num = 0

# Envia o nome do arquivo para o servidor
packet = Packet(seq_num, filename.encode())
packet.add_checksum()
sock.sendto(packet.to_bytes(), (UDP_IP, UDP_PORT))
if Packet.from_bytes(sock.recv(BUFFER_SIZE)).is_corrupt():
    print("Reenviando nome do arquivo...")
else:
    seq_num = 1 - seq_num

# Abre o arquivo que será enviado
with open(filename, "rb") as f:
    # Lê o arquivo em pedaços de tamanho BUFFER_SIZE
    data = f.read(BUFFER_SIZE)
    while data:
        # Envia o pedaço de arquivo para o servidor usando rdt3.0
        packet = Packet(seq_num, data)
        packet.add_checksum()
        if not packet_loss(PACKET_LOSS_PROB):
            sock.sendto(packet.to_bytes(), (UDP_IP, UDP_PORT))
            ack_received = Packet.from_bytes(sock.recv(BUFFER_SIZE)).is_ACK(seq_num)
        else:
            print("Perdendo pacote intencionalmente")
            ack_received = False

        if ack_received:
            seq_num = 1 - seq_num
            data = f.read(BUFFER_SIZE)
        else:
            print("Reenviando pacote...")

received_data = b""
while True:
    try:
        # Recebe um pacote do servidor
        data, addr = sock.recvfrom(BUFFER_SIZE)
        packet = Packet.from_bytes(data)
        if not packet.is_corrupt() and packet.is_ACK(seq_num):
            print(f"Pacote recebido: {packet.get_data().decode()}")
            seq_num = 1 - seq_num
            received_data += packet.get_data()
            if len(packet.get_data()) < BUFFER_SIZE:
                break
        else:
            print(f"Pacote incorreto, enviando ACK anterior")
            packet = Packet(1 - seq_num, b'')
            packet.add_checksum()
            sock.sendto(packet.to_bytes(), addr)
    except socket.timeout:
        print(
            f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
        break

# Salva o arquivo recebido
with open("received_on_client_" + filename, "wb") as f:
    f.write(received_data)

# Fecha o socket
sock.close()
