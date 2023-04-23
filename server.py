import socket
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT
from aux_functions import extract_packet, send_packet, wait_for_ack, send_ack, Packet

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(TIMEOUT_LIMIT)
print("Servidor pronto para receber arquivos...")
filename = ""

try:
    expected_seq_num = 0

    # Recebe o nome do arquivo do cliente
    data, addr = sock.recvfrom(BUFFER_SIZE)
    packet = extract_packet(data)

    if packet.seq_n == expected_seq_num:
        print(f"Nome do arquivo recebido: {packet.data}")
        filename = packet.data
        send_ack(sock, packet.seq_n, addr)
        expected_seq_num = 1 - expected_seq_num
    else:
        print(f"Recebimento incorreto: {packet.seq_n}, enviando ACK anterior")
        send_ack(sock, 1 - expected_seq_num, addr)

    client_fixed_addr = addr
    # Cria um buffer para armazenar o arquivo recebido
    received_data = b""

    # Recebe o arquivo do cliente em pedaços de tamanho BUFFER_SIZE
    while True:
        try:
           # Recebe um pacote do cliente
            data, addr = sock.recvfrom(BUFFER_SIZE)
            packet = extract_packet(data)
            # filename = packet.data
            if packet.seq_n == expected_seq_num:
                # Avalia o checksum dele
                if packet.checksum ==  packet.real_checksum():
                    print(f"Pacote recebido: {packet.seq_n}")
                    send_ack(sock, packet.seq_n, addr)
                    expected_seq_num = 1 - expected_seq_num
                    received_data += packet.data.encode('utf-8')
                    if len(packet.data) + packet.reading_size() < BUFFER_SIZE:
                        break
                else:
                    print(f"Checksum incorreto: {packet.checksum}, esperado: {packet.real_checksum()}")
                    send_ack(sock, 1 - expected_seq_num, addr)
            else:
                print(f"Pacote incorreto: {packet.seq_n}, enviando ACK anterior")
                send_ack(sock, 1 - expected_seq_num, addr)
        except socket.timeout:
            print(
                f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
            break

    # Salva o arquivo recebido
    with open("received_on_server_" + filename, "wb") as f:
        f.write(received_data)

    seq_num = 0

    # Abre o arquivo recebido e armazenado e envia de volta para o cliente em pedaços de tamanho BUFFER_SIZE
    with open("received_on_server_" + filename, "rb") as f:
        packet = Packet(seq_num, False, "")
        data = f.read(BUFFER_SIZE - packet.reading_size())

        while data:
            # Envia o pedaço de arquivo para o cliente usando rdt3.0
            packet = Packet(seq_num, False, data.decode('utf-8'))
            # print(f"Enviando pacote {seq_num}")
            send_packet(sock, packet, client_fixed_addr)
            ack_received = wait_for_ack(sock, seq_num)
            if ack_received:
                seq_num = 1 - seq_num

                packet = Packet(seq_num, False, "")
                data = f.read(BUFFER_SIZE - packet.reading_size())
            else:
                print("Reenviando pacote...")

except socket.timeout:
    f.close()
    print(
        f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")

# Fecha o socket
print('Conexão encerrada.')
sock.close()
