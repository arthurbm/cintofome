import socket
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB, PACKET_LOSS_PROB
from aux_functions import make_packet, extract_data, send_packet, wait_for_ack, send_ack, packet_loss, calculate_checksum

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(TIMEOUT_LIMIT)

print("Servidor pronto para receber arquivos...")
try:
    expected_seq_num = 0

    # Recebe o nome do arquivo do cliente
    data, addr = sock.recvfrom(BUFFER_SIZE)
    recv_seq_num, checksum, filename = extract_data(data)
    if recv_seq_num == expected_seq_num and checksum == calculate_checksum(filename.encode()):
        print(f"Nome do arquivo recebido: {filename}")
        send_ack(sock, recv_seq_num, addr)
        expected_seq_num = 1 - expected_seq_num
    else:
        print(f"Recebimento incorreto: {filename}, enviando ACK anterior")
        send_ack(sock, 1 - expected_seq_num, addr)

    client_fixed_addr = addr
    # Cria um buffer para armazenar o arquivo recebido
    received_data = b""

    # Recebe o arquivo do cliente em pedaços de tamanho BUFFER_SIZE
    while True:
        try:
           # Recebe um pacote do cliente
            data, addr = sock.recvfrom(BUFFER_SIZE)
            recv_seq_num, recv_checksum, packet_data = extract_data(data)
            if recv_seq_num == expected_seq_num:
                # Avalia o checksum dele
                if recv_checksum == calculate_checksum(packet_data.encode()):
                    print(f"Pacote recebido: {packet_data}")
                    send_ack(sock, recv_seq_num, addr)
                    expected_seq_num = 1 - expected_seq_num
                    received_data += packet_data.encode('utf-8')
                    if len(packet_data) < BUFFER_SIZE:
                        break
                else:
                    print(f"Checksum incorreto: {recv_checksum}, esperado: {calculate_checksum(packet_data.encode())}")
                    send_ack(sock, 1 - expected_seq_num, addr)
            else:
                print(f"Pacote incorreto: {packet_data}, enviando ACK anterior")
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
        data = f.read(BUFFER_SIZE)
        while data:
            # Envia o pedaço de arquivo para o cliente usando rdt3.0
            packet = make_packet(seq_num, data.decode('utf-8'))
            # print(f"Enviando pacote {seq_num}")
            send_packet(sock, packet, client_fixed_addr)
            ack_received = wait_for_ack(sock, seq_num)
            if ack_received:
                seq_num = 1 - seq_num
                data = f.read(BUFFER_SIZE)
            else:
                print("Reenviando pacote...")

except socket.timeout:
    f.close()
    print(
        f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")

# Fecha o socket
print('Conexão encerrada.')
sock.close()
