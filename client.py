import socket
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT

# Nome do arquivo que será enviado
filename = "example.txt"

# Cria o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define um tempo limite para receber uma resposta do servidor (em segundos)
sock.settimeout(TIMEOUT_LIMIT)

# Envia o nome do arquivo para o servidor
sock.sendto(filename.encode(), (UDP_IP, UDP_PORT))

# Abre o arquivo que será enviado
with open(filename, "rb") as f:
    # Lê o arquivo em pedaços de tamanho BUFFER_SIZE
    data = f.read(BUFFER_SIZE)
    while data:
        # Envia o pedaço de arquivo para o servidor
        sock.sendto(data, (UDP_IP, UDP_PORT))
        # Lê o próximo pedaço de arquivo
        data = f.read(BUFFER_SIZE)

# Recebe o arquivo de volta do servidor
received_data = b""
while True:
    try:
        # Recebe um pacote do servidor
        data, addr = sock.recvfrom(BUFFER_SIZE)
        # Adiciona o pacote recebido ao dado recebido
        received_data += data
        # Se o pacote recebido tiver menos que BUFFER_SIZE bytes, é o último pacote
        if len(data) < BUFFER_SIZE:
            break
    except socket.timeout:
        # Se o tempo limite expirar, exibe uma mensagem de erro e sai do loop
        print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
        break

# Salva o arquivo recebido
with open("received_client_" + filename, "wb") as f:
    f.write(received_data)

# Fecha o socket
sock.close()
