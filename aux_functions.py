import socket
import random
from constants import BUFFER_SIZE, TIMEOUT_LIMIT

class Packet: 

    def __init__(self, seq_n, is_ack, data, checksum=None):
        self.seq_n = seq_n
        self.is_ack = is_ack
        self.data = data
        self.checksum = checksum
        
        if is_ack == "True":
            is_ack = True
        if is_ack == "False":
            is_ack = False

        if checksum is None:
            self.checksum = self.real_checksum()

    def reading_size(self):
        _checksum = self.real_checksum()
        packet_return = (str(self.seq_n) + "|" + str(_checksum) + "|" + str(self.is_ack) + "|")
        return len(packet_return.encode('utf-8')) + 16 

    def make_packet(self):
        _checksum = self.real_checksum()
        packet_return = (str(self.seq_n) + "|" + str(_checksum) + "|" + str(self.is_ack) + "|" + str(self.data))
        return packet_return

    def real_checksum(self):
        data = str(self.seq_n) + str(self.is_ack) + str(self.data)
        data = data.encode()

        polynomial = 0x1021
        crc = 0xFFFF
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if (crc & 0x8000):
                    crc = (crc << 1) ^ polynomial
                else:
                    crc = (crc << 1)
        return crc & 0xFFFF

    def is_corrupt(self):
        return self.real_checksum() != self.checksum


def extract_packet(string_packet):
    seq_num, checksum_, is_ack, data = string_packet.decode().split("|", 3)
    return Packet(int(seq_num), is_ack, data, checksum=int(checksum_))

def send_packet(sock, packet, addr):
    # print(f"Enviando pacote: {packet.seq_n} de")
    # print(" " + str(len(packet.make_packet().encode('utf-8'))) + " bytes")
    sock.sendto(packet.make_packet().encode(), addr)

def send_ack(sock, seq_num, addr):
    packet = Packet(seq_num, True, 0, 0)
    # print(f"Enviando ACK: {seq_num}")
    sock.sendto(packet.make_packet().encode(), addr)

# def make_ack_packet(seq_num):
#    return (str(seq_num) + "|ACK").encode()

def wait_for_ack(sock, expected_ack):
    try:
        ack = Packet(0, True, "")
        data, _ = sock.recvfrom(BUFFER_SIZE - ack.reading_size())
        ack = extract_packet(data)
        if ack.is_ack and expected_ack == ack.seq_n:
            # print(f"ACK recebido: {ack.seq_n}")
            return True
        else:
            # print(f"ACK incorreto: {ack.seq_n}, esperado: {expected_ack}")
            # exit()
            return False
    except socket.timeout:
        # print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido.")
        return False

def packet_loss(probability):
    return random.random() < probability

def chunk_divide(data, head_size):
    data_bytes = data.encode('utf-8')

    chunk_size = BUFFER_SIZE - head_size

    chunks = [data_bytes[i:i+chunk_size] for i in range(0, len(data_bytes), chunk_size)]

    return chunks

def sock_receive(sock, expected_seq_num):
    received_data = "".encode('utf-8')

    while True:
        try:
           # Recebe um pacote 
            data, addr = sock.recvfrom(BUFFER_SIZE)
            packet = extract_packet(data)
            # filename = packet.data
            if packet.seq_n == expected_seq_num:
                # Avalia o checksum dele
                if packet.checksum ==  packet.real_checksum():
                    # print(f"Pacote recebido: {packet.seq_n}")
                    send_ack(sock, packet.seq_n, addr)
                    expected_seq_num = 1 - expected_seq_num
                    received_data += packet.data.encode('utf-8')
                    if len(packet.data) + packet.reading_size() < BUFFER_SIZE:
                        break
                else:
                    # print(f"Checksum incorreto: {packet.checksum}, esperado: {packet.real_checksum()}")
                    send_ack(sock, 1 - expected_seq_num, addr)
            else:
                # print(f"Pacote incorreto: {packet.seq_n}, enviando ACK anterior")
                send_ack(sock, 1 - expected_seq_num, addr)
        except socket.timeout:
            # print(
                # f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
            data = ""
            addr = ""
            break

    return data, expected_seq_num, addr 

def sock_send(message, sock, seq_num, addr):

    packet = Packet(seq_num, False, "")

    chunks = chunk_divide(message, packet.reading_size()) 

    for data in chunks:
        while True:
            # Envia o pedaço de arquivo para o cliente usando rdt3.0
            packet = Packet(seq_num, False, data.decode('utf-8'))
            # # print(f"Enviando pacote {seq_num}")
            send_packet(sock, packet, addr)
            ack_received = wait_for_ack(sock, seq_num)
            if ack_received:
                seq_num = 1 - seq_num

                packet = Packet(seq_num, False, "")
                break
            else:
                print()
    
    return seq_num