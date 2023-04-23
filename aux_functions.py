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
        return len(packet_return.encode('utf-8')) + 32

    def make_packet(self):
        _checksum = self.real_checksum()
        packet_return = (str(self.seq_n) + "|" + str(_checksum) + "|" + str(self.is_ack) + "|" + str(self.data))
        print("Pacote de " + str(len(packet_return.encode('utf-8'))) + " bytes")
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
    print(f"Enviando pacote: {packet.make_packet()}")
    sock.sendto(packet.make_packet().encode(), addr)

def send_ack(sock, seq_num, addr):
    packet = Packet(seq_num, True, 0, 0)
    print(f"Enviando ACK: {seq_num}")
    sock.sendto(packet.make_packet().encode(), addr)

# def make_ack_packet(seq_num):
#    return (str(seq_num) + "|ACK").encode()

def wait_for_ack(sock, expected_ack):
    try:
        ack = Packet(0, True, "")
        data, _ = sock.recvfrom(BUFFER_SIZE - ack.reading_size())
        ack = extract_packet(data)
        if ack.is_ack and expected_ack == ack.seq_n:
            print(f"ACK recebido: {ack.seq_n}")
            return True
        else:
            print(f"ACK incorreto: {ack.seq_n}, esperado: {expected_ack}")
            exit()
            return False
    except socket.timeout:
        print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido.")
        return False

def packet_loss(probability):
    return random.random() < probability
