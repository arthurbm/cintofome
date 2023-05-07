from socket import *
from rdt import *
from aux_functions import extract_packet

#instanciando um cliente
RDTSocket = RDT()

#mensagem vazia pra o contato com servidor
data = ''

while True:
  
  RDTSocket.send(data)

  msg = RDTSocket.receive()
  msg = extract_packet(msg.encode()).data

  #receber 'ok', encerra a conexão
  if('ok' == msg):
    break
  
  data = input(msg)

msg = RDTSocket.receive()
msg = extract_packet(msg.encode()).data
print(msg)

RDTSocket.close_connection()