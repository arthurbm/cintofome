import socket

# Endereço IP e porta que o servidor irá escutar
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Tamanho do buffer em bytes
BUFFER_SIZE = 1024

# Cria o socket UDP e associa ele ao endereço IP e porta definidos
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Servidor pronto para receber arquivos...")

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
with open("received_" + filename, "wb") as f:
    f.write(received_data)

# Abre o arquivo recebido e envia ele de volta para o cliente em pedaços de tamanho BUFFER_SIZE
with open("received_" + filename, "rb") as f:
    data = f.read(BUFFER_SIZE)
    while data:
        sock.sendto(data, addr)
        data = f.read(BUFFER_SIZE)

# Fecha o socket
sock.close()
