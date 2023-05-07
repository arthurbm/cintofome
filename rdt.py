from socket import *
import time
from aux_functions import extract_packet, send_packet, wait_for_ack, send_ack, packet_loss, Packet, chunk_divide, sock_send, sock_receive
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB

class RDT:
  #projeto ja se inicia com valores pré-setados
  def __init__(self, isServer = 0, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
    self.sender_addr = 0
    self.seq_num = 0 
    self.addressPort = addressPort
    self.bufferSize = bufferSize
    self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
    self.isServer = isServer

  #faz a checagem pra ver se trata de um servidor, caso sim alocamos uma porta e um endereçoIP para o pacote
    if isServer:
        self.UDPSocket.bind(self.addressPort)
        self.UDPSocket.settimeout(2.0)
        """print("Server running")"""
    else:
        """ print("Client running") """

  #função para transferencia de pacotes
  def send(self, data):
    if self.isServer:
        """ print("Sending to client") """
        # self.UDPSocket.sendto(data, self.sender_addr)
        self.seq_num = sock_send(data, self.UDPSocket, self.seq_num, self.sender_addr)
    else:
        """ print("Sending to server") """
        #self.UDPSocket.sendto(data, self.addressPort)
        self.seq_num = sock_send(data, self.UDPSocket, self.seq_num, self.addressPort)
  
  #Funcao de recepcao de pacotes entre cliente e servidor
  def receive(self):
    """ print("Receveing package") """
    self.UDPSocket.settimeout(20.0) 
    # data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
    data, self.seq_num, self.sender_addr = sock_receive(self.UDPSocket, self.seq_num)

    if data != "":
      
      """ print("Received") """
      return data.decode('utf-8')

  #Funcao que encerra a conexao
  def close_connection(self):
    """ print("Closing socket") """
    self.UDPSocket.close()