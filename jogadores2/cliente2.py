import socket  # Cria o socket, conecta com o servidor e envia/recebe dados
import threading  # Permite que múltiplas tarefas sejam executadas simultaneamente

HOST = "10.149.148.55"  # IP do servidor
PORT = 4000  # Porta usada pela aplicação

# Função de receber mensagens. É responsável por "escutar" o servidor continuamente.
def receber_mensagens(cliente):
    while True:  # Mantém o loop de escuta sempre ativo
        try: 
            # recv() recebe dados de até 1024 bytes; decode() transforma bytes em string
            mensagem = cliente.recv(1024).decode('utf-8')
            
            # Verifica se chegou alguma mensagem. Se o retorno for vazio, significa
            # que o servidor fechou a conexão de forma limpa.
            if not message: 
                break  # Sai do laço de repetição para encerrar a thread
                
            print(mensagem)  # Exibe a mensagem que o servidor enviou no terminal
        except: 
            # Caso a conexão caia ou o socket seja fechado abruptamente, a thread encerra
            break

# Cria o socket TCP: AF_INET define o uso de IPv4 e SOCK_STREAM define o uso de TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
    # Bloco de proteção contra erros de conexão
    try:
        # Realiza a conexão com o servidor (dispara o processo de Three-way Handshake: SYN, SYN-ACK, ACK)
        cliente.connect((HOST, PORT)) 
        print("Conectado ao servidor.")
        
        # Cria uma thread paralela para processar as mensagens de entrada
        thread = threading.Thread(
            target=receber_mensagens,  # Indica a função que a thread executará em paralelo
            args=(cliente,)  # Passa o socket do cliente como argumento para a função
        )
        
        # Define a thread como Daemon. Isso faz com que ela rode em segundo plano e seja
        # finalizada automaticamente pelo Sistema Operacional assim que o programa principal fechar.
        thread.daemon = True 
        thread.start()  # Inicializa a execução da thread
        
        # Loop principal para capturar o input do usuário
        while True: 
            # input() lê o teclado; strip() remove espaços extras; lower() padroniza em minúsculo
            jogada = input(">> ").strip().lower()
            
            # Tratamento para o comando de saída do jogo
            if jogada == "sair":
                # sendall() garante que todos os bytes sejam entregues sem fragmentação na camada de transporte
                # encode() transforma a string em bytes para que o protocolo TCP possa transmitir
                cliente.sendall(jogada.encode('utf-8'))
                print("Você saiu do jogo.")
                break  # Sai do loop principal, finalizando o bloco 'with' e fechando o socket
                
            # Validação local básica da jogada antes de gastar recursos de rede
            if jogada not in ['pedra', 'papel', 'tesoura']:
                print("Jogada inválida.")
                print("Use: pedra, papel ou tesoura")
                continue  # Reinicia o loop atual sem enviar nada ao servidor
                
            # Envia a jogada válida codificada em bytes para o servidor via TCP
            cliente.sendall(jogada.encode('utf-8'))
            
    except ConnectionRefusedError: 
        # Exceção específica acionada quando o servidor está offline ou a porta está fechada
        print("Servidor não encontrado.")
    except: 
        # Captura qualquer outra anomalia ou falha genérica na comunicação
        print("Erro na conexão.")
