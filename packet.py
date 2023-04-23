import random
import socket
import struct

class Packet:
    def __init__(self, seq_num, data):
        self.seq_num = seq_num
        self.data = data
        self.checksum = self.calc_checksum()

    @classmethod
    def from_bytes(cls, packet_bytes):
        seq_num, checksum = struct.unpack('!2I', packet_bytes[:8])
        data = packet_bytes[8:].decode('utf-8')
        packet = cls(seq_num, data)
        return packet, checksum

    def to_bytes(self):
        packet_bytes = struct.pack('!2I', self.seq_num, self.checksum) + self.data.encode('utf-8')
        return packet_bytes

    def calc_checksum(self):
        data = self.to_bytes()
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
        return self.calc_checksum() != 0

    @staticmethod
    def packet_loss(probability):
        return random.random() < probability

    @staticmethod
    def send_packet(sock, packet, addr):
        print(f"Enviando pacote: {packet}")
        sock.sendto(packet, addr)

    @staticmethod
    def send_ack(sock, seq_num, addr):
        ack_packet = Packet(seq_num, "ACK")
        print(f"Enviando ACK: {seq_num}")
        sock.sendto(ack_packet.to_bytes(), addr)

    @staticmethod
    def wait_for_ack(sock, expected_ack):
        try:
            data, addr = sock.recvfrom(1024)
            packet, checksum = Packet.from_bytes(data)
            ack = packet.seq_num
            if not packet.is_corrupt() and ack == expected_ack and packet.data == "ACK":
                print(f"ACK recebido: {ack}")
                return True
            else:
                print(f"Pacote incorreto: {packet.data}, enviando ACK anterior")
                Packet.send_ack(sock, 1 - expected_ack, addr)
                return False
        except socket.timeout:
            print(f"Tempo limite de 5 segundos atingido.")
            return False
