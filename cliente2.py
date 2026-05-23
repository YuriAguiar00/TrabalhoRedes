import socket #cria socket, conecta com servidor, envia/recebe dados
import threading #as threads permitem tarefas múltiplas executadas 
HOST = "10.149.148.55" # ip do roteador do yuri
PORT = 4000 #porta usada pela aplicação
# função de receber mensagens. é responsável por "escutar" o servidor sempre
def receber_mensagens(cliente):
    while True: #faz com que o loop esteja sempre ativo 
        try: 
            # cliente recv recebe dados com até 1024 bytes, decote transforma bytes em string
            mensagem = cliente.recv(1024).decode('utf-8')
            if not mensagem: # essa linha é para "ver" se chega mensagem, se nçao chegar, quer dizer que o servidor fechou, ou seja, sem loops ou threads
                break # se o servidor estiver fechado, saí da repetição
            print(mensagem) #mostra a mensagem que o servidor enviou
        except: #caso conexão caia, servidor feche, sockete feche, a thread encerra
            break
#cria o sockete TCP, AF_INET é ipva e SOCK_STREAM é TCP/ toda vez que isso for verdade inicia o loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
   # Proteção contra erro:
    try:
        #three-way handshake
        cliente.connect((HOST, PORT)) # SYN, SYN-ACK, ACK
        print("Conectado ao servidor.")
        # cria uma thread  paralela
        thread = threading.Thread(
            target=receber_mensagens, #o target serve para indicar a função que a thread executará, no caso, receber_mensagens
            args=(cliente,) # argumentos enviados, nesse código leva o socket cliente (principal)
        )
        thread.daemon = True #essa função funciona em segundo plano no python e atua "matando" a thread inteira caso o programa feche
        thread.start() #inicializa thread
        
        while True: 
            #input lê o telcado, strip remove o que nçao for caractere, lower transforma tudo em minusculo
            jogada = input(">> ").strip().lower()
            #caso o cliente digite sair, ele printa na tela e sai do loop
            if jogada == "sair":
                #o sendall ou send all garante que todos os bytes sejam entregues, ou seja, a mensagem não se perde e o programa executa toda a função
                # encode é responsavel por transformar string em bytes para que o tcp transmita
                cliente.sendall(jogada.encode('utf-8'))
                print("Você saiu do jogo.")
                break
            #validação básica ada jogada, se não for um coisa válida não serve
            if jogada not in ['pedra', 'papel', 'tesoura']:
                print("Jogada inválida.")
                print("Use: pedra, papel ou tesoura")
                continue #reinicia o loop sem que nada seja enviado
            #mesma coisa do comando de saída, sendall para não perder nada e encode para transformar em bytes o string.
            cliente.sendall(jogada.encode('utf-8'))
    except ConnectionRefusedError: #exceção específica do python para servidor desligado, ip errado e prota errada
        print("Servidor não encontrado.")
    except: #exceção para qualquer outro tipo de erro
        print("Erro na conexão.")
