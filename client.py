import socket
import time
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB
from aux_functions import make_packet, extract_data, send_packet, wait_for_ack, send_ack, packet_loss, Packet

filename = "example.txt"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define um tempo limite para receber uma resposta do servidor (em segundos)
sock.settimeout(TIMEOUT_LIMIT)

seq_num = 0

# Envia o nome do arquivo para o servidor
packet = make_packet(seq_num, filename)
send_packet(sock, packet, (UDP_IP, UDP_PORT))
if wait_for_ack(sock, seq_num):
    seq_num = 1 - seq_num
else:
    print("Reenviando nome do arquivo...")

# Abre o arquivo que será enviado
with open(filename, "rb") as f:
    # Lê o arquivo em pedaços de tamanho BUFFER_SIZE
    data = f.read(BUFFER_SIZE)
    while data:
        # Envia o pedaço de arquivo para o servidor usando rdt3.0
        packet = make_packet(seq_num, data.decode('utf-8'))
        if not packet_loss(PACKET_LOSS_PROB):
            send_packet(sock, packet, (UDP_IP, UDP_PORT))
            ack_received = wait_for_ack(sock, seq_num)
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
        recv_seq_num, recv_checksum, packet_data = extract_data(data)
        if recv_seq_num == seq_num:
            # Avalia o checksum dele
            if recv_checksum == Packet.real_checksum(packet_data.encode()):
                print(f"Pacote recebido: {packet_data}")
                send_ack(sock, recv_seq_num, addr)
                seq_num = 1 - seq_num
                received_data += packet_data.encode('utf-8')
                if len(packet_data) < BUFFER_SIZE:
                    break
            else:
                print(f"Checksum incorreto: {recv_checksum}, esperado: {Packet.real_checksum(packet_data.encode())}")
                send_ack(sock, 1 - seq_num, addr)
        else:
            print(f"Pacote incorreto: {packet_data}, enviando ACK anterior")
            send_ack(sock, 1 - seq_num, addr)
    except socket.timeout:
        print(
            f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
        break

# Salva o arquivo recebido
with open("received_on_client_" + filename, "wb") as f:
    f.write(received_data)

# Fecha o socket
sock.close()
