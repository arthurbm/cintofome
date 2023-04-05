import socket
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT

# Cria o socket UDP e associa ele ao endereço IP e porta definidos
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Define o tempo máximo de espera pelo recebimento de dados como 10 segundos
sock.settimeout(TIMEOUT_LIMIT)

print("Servidor pronto para receber arquivos...")

try:
    # Recebe o nome do arquivo do cliente
    data, addr = sock.recvfrom(BUFFER_SIZE)
    filename = data.decode()

    # Cria um buffer para armazenar o arquivo recebido
    received_data = b""

    client_fixed_addr = None

    # Recebe o arquivo do cliente em pedaços de tamanho BUFFER_SIZE
    while True:
        # Recebe um pacote do cliente
        data, addr = sock.recvfrom(BUFFER_SIZE)
        # Armazena o endereço do cliente se ainda não foi armazenado
        if client_fixed_addr is None:
            client_fixed_addr = addr
        # Adiciona o pacote recebido ao dado recebido
        received_data += data
        # Se o pacote recebido tiver menos que BUFFER_SIZE bytes, é o último pacote
        if len(data) < BUFFER_SIZE:
            break

    # Salva o arquivo recebido
    with open("received_server_" + filename, "wb") as f:
        extra_message_client = "-> received from client"
        f.write(received_data + extra_message_client.encode())

    # Abre o arquivo recebido e envia ele de volta para o cliente em pedaços de tamanho BUFFER_SIZE
    with open(filename, "rb") as f:
        data = f.read(BUFFER_SIZE)
        while data:
            extra_message_server = " -> received from server"
            sock.sendto(data + extra_message_server.encode(), client_fixed_addr)
            data = f.read(BUFFER_SIZE)

except socket.timeout:
    f.close()
    print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")

# Fecha o socket
print('Conexão encerrada.')
sock.close()
