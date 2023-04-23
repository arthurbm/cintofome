import socket
import random
from constants import BUFFER_SIZE, TIMEOUT_LIMIT

class Packet: 

    def __init__(self, seq_n, ack_n, data, checksum):
        self.seq_n = seq_n
        self.ack_n = ack_n
        self.data = data
        self.checksum = checksum

    def make_packet(self):
        return (str(self.seq_n) + "|" + str(self.ack_n) + "|" + str(self.data))

    # TODO: implement is_ack, checksum and is_corrupt
    def is_ACK():
        

    def real_checksum():
        return  

    def is_corrupt(self):
        return self.real_checksum() != self.checksum


def make_packet(seq_num, checksum, data):
    return (str(seq_num) + "|" + data).encode()

def extract_data(packet):
    seq_num, data = packet.decode().split("|", 1)
    return int(seq_num), data

def extract_seq_num(packet):
    seq_num, _ = packet.decode().split("|", 1)
    return int(seq_num)

def send_packet(sock, packet, addr):
    print(f"Enviando pacote: {packet.decode()}")
    sock.sendto(packet, addr)

def send_ack(sock, seq_num, addr):
    ack_packet = make_ack_packet(seq_num)
    print(f"Enviando ACK: {seq_num}")
    sock.sendto(ack_packet, addr)

def make_ack_packet(seq_num):
    return (str(seq_num) + "|ACK").encode()

def wait_for_ack(sock, expected_ack):
    try:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        ack = int(data.decode().split("|")[0])
        if ack == expected_ack:
            print(f"ACK recebido: {ack}")
            return True
        else:
            print(f"ACK incorreto: {ack}, esperado: {expected_ack}")
            return False
    except socket.timeout:
        print(f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido.")
        return False

def packet_loss(probability):
    return random.random() < probability
