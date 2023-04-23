import socket
import random
import zlib
from constants import BUFFER_SIZE, TIMEOUT_LIMIT

def make_packet(seq_num, data):
    checksum = zlib.crc32(data.encode('utf-8'))
    return (f"{seq_num}|{checksum}|{data}").encode()

def extract_data(packet):
    seq_num, recv_checksum, data = packet.decode().split("|", 2)
    recv_checksum = int(recv_checksum)
    calculated_checksum = zlib.crc32(data.encode('utf-8'))

    if recv_checksum == calculated_checksum:
        return int(seq_num), data
    else:
        return None, None  # Indicando que o pacote está corrompido

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
    return (f"{seq_num}|ACK").encode()

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
