import socket
import threading
#ip de teste
HOST = "127.0.0.1"
# Porta do servidor
PORT = 4000
# receber o que foi feito na tela (presta atenção aq gustavo)
def receber_mensagens(socket_cliente):
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode('utf-8')
            if not mensagem:
                print("\nConexão encerrada pelo servidor.")
                break

            print(mensagem)

        except:

            print("\nErro na conexão.")
            break
# cleinte 1 usando ipv4 e tcp
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    try:
        # faz o three handshake e confrima conexão
        cliente.connect((HOST, PORT))
        print("Conectado ao servidor.")

        # fila de concorrência para recebimentod e mnesagens
        thread_recebimento = threading.Thread(
            target=receber_mensagens,
            args=(cliente,)
        )
        thread_recebimento.daemon = True
        thread_recebimento.start()
        # quanto tudo tiver ok, executra o passo de while
        while True:
            jogada = input(">> ").lower()

            # sair
            if jogada == "sair":
                cliente.sendall(jogada.encode('utf-8'))
                print("Você saiu do jogo.")
                break
            # valdia jogada
            if jogada not in ['pedra', 'papel', 'tesoura']:
                print("Jogada inválida.")
                print("Use: pedra, papel ou tesoura")
                continue

            # envia a jogada como caractere 
            cliente.sendall(jogada.encode('utf-8'))
    #exceção caso servidor não esteja aberto
    except ConnectionRefusedError:
        print("Servidor não encontrado.")
    #exceção caso erro de verdade na conexâo
    except:
        print("Erro na conexão.")