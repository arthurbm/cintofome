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

    # Recebe o arquivo do cliente em pedaços de tamanho BUFFER_SIZE
    while True:
        # Recebe um pacote do cliente
        data, addr = sock.recvfrom(BUFFER_SIZE)
        # Adiciona o pacote recebido ao dado recebido
        received_data += data
        # Se o pacote recebido tiver menos que BUFFER_SIZE bytes, é o último pacote
        if len(data) < BUFFER_SIZE:
            break

    # Salva o arquivo recebido
    with open("received_server_" + filename, "wb") as f:
        f.write(received_data)

    # Abre o arquivo recebido e envia ele de volta para o cliente em pedaços de tamanho BUFFER_SIZE
    with open("received_server_" + filename, "rb") as f:
        data = f.read(BUFFER_SIZE)
        while data:
            sock.sendto(data, addr)
            data = f.read(BUFFER_SIZE)

except socket.timeout:
    print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")

# Fecha o socket
sock.close()
