import socket
import packet
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB, PACKET_LOSS_PROB

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(TIMEOUT_LIMIT)

print("Servidor pronto para receber arquivos...")
try:
    expected_seq_num = 0

    # Recebe o nome do arquivo do cliente
    data, addr = sock.recvfrom(BUFFER_SIZE)
    packet, checksum = packet.Packet.from_bytes(data)
    recv_seq_num = packet.seq_num
    filename = packet.data
    if not packet.is_corrupt() and recv_seq_num == expected_seq_num:
        print(f"Nome do arquivo recebido: {filename}")
        packet.Packet.send_ack(sock, recv_seq_num, addr)
        expected_seq_num = 1 - expected_seq_num
    else:
        print(f"Nome do arquivo incorreto: {filename}, enviando ACK anterior")
        packet.Packet.send_ack(sock, 1 - expected_seq_num, addr)

    client_fixed_addr = addr
    # Cria um buffer para armazenar o arquivo recebido
    received_data = b""

    # Recebe o arquivo do cliente em pedaços de tamanho BUFFER_SIZE
    while True:
        try:
            # Recebe um pacote do cliente
            data, addr = sock.recvfrom(BUFFER_SIZE)
            packet, checksum = packet.Packet.from_bytes(data)
            recv_seq_num = packet.seq_num
            packet_data = packet.data
            if not packet.is_corrupt() and recv_seq_num == expected_seq_num:
                print(f"Pacote recebido: {packet_data}")
                packet.Packet.send_ack(sock, recv_seq_num, addr)
                expected_seq_num = 1 - expected_seq_num
                received_data += packet_data.encode('utf-8')
                if len(packet_data) < BUFFER_SIZE:
                    break
            else:
                print(f"Pacote incorreto: {packet_data}, enviando ACK anterior")
                packet.Packet.send_ack(sock, 1 - expected_seq_num, addr)
        except socket.timeout:
            print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
            break

    # Salva o arquivo recebido
    with open("received_on_server_" + filename, "wb") as f:
        f.write(received_data)

    seq_num = 0

    # Abre o arquivo recebido e armazenado e envia de volta para o cliente em pedaços de tamanho BUFFER_SIZE
    with open("received_on_server_" + filename, "rb") as f:
        data = f.read(BUFFER_SIZE)
        while data:
            # Envia o pedaço de arquivo para o cliente usando rdt3.0
            packet = packet.Packet(seq_num, data.decode('utf-8'))
            if not packet.Packet.packet_loss(PACKET_LOSS_PROB):
                packet.Packet.send_packet(sock, packet.to_bytes(), client_fixed_addr)
                ack_received = packet.Packet.wait_for_ack(sock, seq_num)
            else:
                print("Perdendo pacote intencionalmente")
                ack_received = False

            if ack_received:
                seq_num = 1 - seq_num
                data = f.read(BUFFER_SIZE)
            else:
                print("Reenviando pacote...")
                print("Reenviando pacote...")

except socket.timeout:
    f.close()
    print(
        f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")

# Fecha o socket
print('Conexão encerrada.')
sock.close()
