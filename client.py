import socket
import time
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT
from aux_functions import make_packet, extract_data, send_packet, wait_for_ack, send_ack

filename = "example.txt"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
        packet = make_packet(seq_num, data.decode('latin1'))
        send_packet(sock, packet, (UDP_IP, UDP_PORT))
        if wait_for_ack(sock, seq_num):
            seq_num = 1 - seq_num
            data = f.read(BUFFER_SIZE)
        else:
            print("Reenviando pacote...")

received_data = b""
while True:
    try:
        # Recebe um pacote do servidor
        data, addr = sock.recvfrom(BUFFER_SIZE)
        recv_seq_num, packet_data = extract_data(data)
        if recv_seq_num == seq_num:
            print(f"Pacote recebido: {packet_data}")
            send_ack(sock, recv_seq_num, addr)
            seq_num = 1 - seq_num
            received_data += packet_data.encode('latin1')
            if len(packet_data) < BUFFER_SIZE:
                break
        else:
            print(f"Pacote incorreto: {packet_data}, enviando ACK anterior")
            send_ack(sock, 1 - seq_num, addr)
    except socket.timeout:
        print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
        break

# Salva o arquivo recebido
with open("received_client_" + filename, "wb") as f:
  f.write(received_data)

# Fecha o socket
sock.close()