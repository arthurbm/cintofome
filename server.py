from socket import *
from rdt import *
from datetime import *
from utils import *
from aux_functions import extract_packet

#pega a hora e formata (horario)
def hour():
    clock = datetime.now()
    return clock.strftime("%X")[:5]

#pedidos feitos (pedidos)
orders = {}

#mostra o cardapio (showCardapio)
def showMenu():
    card = ''
    for x, y in menu.items():
        card = card + " " + str(x) + " " + str(y[0]) + " " + " " + str(y[1]) + "\n"
    return card

#adiciona o pedido ao banco de dados de acordo com o cliente (pedido)
def allOrders(table, client, data):

  #pega o item do cardapio que foi pedido
  food = menu.get(int(data))

  #adiciona o pedido,e atualiza o valor na conta da mesa e do cliente
  orders[table][client]["pedidos"].append(food)
  orders[table]["total"] += float(food[1])
  orders[table][client]["comanda"] += float(food[1])
  
#retorna os pedidos de um cliente específico, e o valor total do pedidos (pedir_conta)	
def getOrdersByClient(table, client):
  total = '\n'
  value = orders[table][client]["comanda"]

  for produto in orders[table][client]["pedidos"]:
    total += f"{produto[0]} {str(produto[1])} \n"
  
  return total,value

#objeto RDT instanciado, indicando ser um servidor
RDTSocket = RDT(1)
data = RDTSocket.receive()
data = extract_packet(data.encode()).data

#espera a mensagem 'chefia'
data = hour() + " cliente: "
RDTSocket.send(data)
data = RDTSocket.receive()
data = extract_packet(data.encode()).data

#continua o mesmo processo, enquanto não receber um `chefia`
while(data != "chefia"):
  data = hour() + "CINtofome: escreva chefia para receber o atendimento!\n"
  data += hour() + " cliente: "
  RDTSocket.send(data)
  data = RDTSocket.receive()
  data = extract_packet(data.encode()).data

#espera o cliente pedir uma mesa, e armazena a info
data = hour() + " CINtofome: Digite Sua mesa\n" + hour() + " cliente: "
RDTSocket.send(data)
data = RDTSocket.receive()
data = extract_packet(data.encode()).data
table = data

#espera o cliente dizer o nome, e armazena a info
data = hour() + " CINtofome: Digite Seu nome: \n" + hour() + " cliente: "
RDTSocket.send(data)
data = RDTSocket.receive()
data = extract_packet(data.encode()).data
name = data

#tupla com IP e porta do cliente
ipPorta = RDTSocket.sender_addr

#insere mesa
if table not in orders:
  orders[table] = {
    "total": 0.0 
    }
  
#insere cliente
orders[table].update({
  name: {
      "nome": name, 
      "comanda": 0.0,
      "socket": ipPorta,
      "pedidos": []
    }
  })

#informa os comandos disponiveis do ChatBot
data = f"{hour()} CINtofome: Digite uma das opcoes a seguir (ou numero ou por extenso) \n {options}\n{hour()} {name}: "
RDTSocket.send(data)

payment = True

#pós cadastro, entra num loop até receber o comando levantar
while True:
  #recebe o comando do cliente
  data = RDTSocket.receive()
  data = extract_packet(data.encode()).data

  match data:
    #opção para mostrar o cardápio
    case '1' | 'cardápio' | 'cardapio':
      res = hour() + " CINtofome:\n" + showMenu() + hour() + " " + name + ": "
      RDTSocket.send(res)
    #opção para fazer o pedido
    case '2' | 'pedir':
      res = hour() + " CINtofome: Digite o primeiro item que gostaria (número) \n" + hour() +" " + name +": "  
      RDTSocket.send(res)
      data = RDTSocket.receive()
      data = extract_packet(data.encode()).data
      #entra num loop, enquanto o cliente não encerrar o pedido com o comando "não", o server continua perguntando se tem mais algo
      flag = True
      while flag:
        allOrders(table,name,data)

        resp = hour() + " CINtofome : Gostaria de mais algum item? (número ou por extenso) \n" + hour() +" " + name + ": "
        RDTSocket.send(resp)
        data = RDTSocket.receive()
        data = extract_packet(data.encode()).data 

        if(str(data) == "nao"):
          flag = False
      resp = hour() + " CINtofome: É pra já! \n" + hour() +" " + name + ": "
      RDTSocket.send(resp)
      payment = False

    #opção para a conta ser apenas do cliente em contato com o servidor
    case '3' | 'conta individual':
      total,value = getOrdersByClient(table,name)
      res = f"CINtofome: Sua conta total é:\n{total}-------------\nValor: {str(value)}"
      res += f"\n{hour()} {name}: "
      RDTSocket.send(res)

    #opção para a conta ser de toda a mesa, na qual está sentado o cliente em contato com o servidor
    case '4' | 'conta da mesa':
      total_orders = str(orders[table]["total"])
      res = f"CINtofome:\n"

      for client in orders[table]:
        if client != "total":
          total,value = getOrdersByClient(table,client)
          if value > 0:
            res += f"\n{client}\n{total}-------------\nValor: {str(value)}\n-------------"
        res += f"\nValor total da mesa: {total_orders}" 
        res += f"\n{hour()} {name}: "
      RDTSocket.send(res)

    #opção para que seja realizado o pagamento
    case '5' | 'pagar':
      bill = orders[table][name]["comanda"]
      closed = orders[table]["total"]
      isValid = False
      dif = 0

      #mostra o valor tal da conta do cliente, e da mesa. e aguarda o comando de pagamento
      base = f"Sua conta foi {bill} e a da mesa foi {closed}. Digite o valor a ser pago. \n{hour()} {name}: "
      res = f"{hour()} CINtofome: {base}"
      RDTSocket.send(res)
      data = RDTSocket.receive()
      data = extract_packet(data.encode()).data 

      #loop para validação do pagamento 
      while True:
        if str(data) == 'nao':  
          res = f"{hour()} CINtofome: Operação de pagamento cancelada!\n"
          break

        if (isValid and str(data) == 'sim'):   
          #remove pedido dos clientes da tabela     
          orders[table][name]["comanda"] = 0.0
          orders[table][name]["pedidos"] = []
          orders[table]["total"] -= bill

          #calculo do troco
          if dif > 0: 
            orders[table]["total"] -= dif
    
            #mostra e divide o valor extra dos clientes com pendencia
            pendingBill = [c for c in orders[table] if c != "total" and orders[table][c]["comanda"] > 0]
            dif_ind = dif/len(pendingBill)

            for client in pendingBill:
              orders[table][client]["comanda"] -= dif

          res = f"{hour()} CINtofome: Conta paga, obrigado! \n" 
          payment = True
          break
        # Se tiver inserido um valor válido
        if (float(data) > bill) and float(data) <= closed:  
          dif = float(data) - bill
          res = f"{hour()} Cintofome: Você está pagando {dif} a mais que sua conta.\n{hour()} Cintofome: O valor excedente será distribuído.\n{hour()} Cintofome: "
          isValid = True
          RDTSocket.send(resp)
        # Pagamento exato
        elif (float(data) == bill): 
          res = f"{hour()} Cintofome: "
          isValid = True
        # Se tiver inserido um valor maior do que a conta da mesa
        elif (float(data) > closed): 
          res = f"{hour()} Cintofome: Valor maior do que o esperado, no momento não aceitamos gorjetas. \n" + base
        # Se tiver inserido um valor menor que a conta individual
        elif (float(data) < bill): 
          res = f"{hour()} Cintofome: Pagamento menor que o devido, nao fazemos fiado. \n" + base

        if isValid:
          res += f"Deseja confirmar o pagamento? (digite sim para confirmar)\n{hour()} {name}: "

        RDTSocket.send(res)
        data = RDTSocket.receive()
        print(data)
        data = extract_packet(data.encode()).data
        print(data)

      res += f"{hour()} {name}: "
      RDTSocket.send(res)

    #opção para levantar e encerrar conexão
    case '6' | 'levantar':
      #se não tiver pago, nn permite encerrar a conexão
      if(not payment):
        res = hour() + " " + name + ": Você ainda não pagou sua conta\n" + hour() + " " + name + ": "
        RDTSocket.send(res)

      #se tiver pago, libera o cliente e encerra conexão
      if(payment):
        res = "ok"
        del orders[table][name]
        RDTSocket.send(res)
        break
    
    case _:
      res = hour() + " " + name + ": Escolha uma das opções possíveis!\n" + hour() + " " + name + ": "
      RDTSocket.send(res)

# se despede termina a conexão
data = hour() + " " + name + ": Volte sempre ^^ \n"
RDTSocket.send(data)

RDTSocket.close_connection()