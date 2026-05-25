import socket  # Biblioteca responsável pela comunicação em rede
import threading  # Permite múltiplas tarefas simultâneas

HOST = "10.149.148.55"  # IP do servidor
PORT = 4000  # Porta da aplicação

# Lista que guarda os sockets dos jogadores (o 'conn' dos usuários).
# Cada elemento é um socket TCP (conexão de rede).
clientes = [] 
jogadas = {}  # Armazena as jogadas da rodada atual

# Lock impede que duas threads alterem dados ao mesmo tempo
lock = threading.Lock()

# Barrier sincroniza os dois jogadores.
# Só continua quando os dois chegarem nela (tratamento de erro de dessincronização).
barreira = threading.Barrier(2)

# Jogadas válidas
opcoes = ['pedra', 'papel', 'tesoura']

# Função responsável por definir o vencedor
def determinar_vencedor(j1, j2):
    # Caso de empate
    if j1 == j2:
        return "empate"
    # Regras de vitória do jogador 1
    elif (j1 == 'pedra' and j2 == 'tesoura') or \
         (j1 == 'papel' and j2 == 'pedra') or \
         (j1 == 'tesoura' and j2 == 'papel'):
        return "jogador1"
    # Inverso: jogador 2 vence
    else:
        return "jogador2"

# Função para enviar mensagens para os clientes
def enviar(cliente, mensagem):
    # encode() transforma string em bytes
    # sendall() garante o envio completo dos dados
    cliente.sendall(mensagem.encode('utf-8'))

# Função principal de cada jogador.
# Cada cliente conectado ganha uma thread exclusiva.
def gerenciar_cliente(cliente, numero_jogador):
    global jogadas
    try:
        # Se ainda não houver dois jogadores conectados
        if len(clientes) < 2:
            enviar(cliente, "Esperando outro jogador...\n")
        
        # Espera (bloqueia o fluxo) até o segundo jogador entrar
        while len(clientes) < 2:
            pass
            
        # Mensagens iniciais enviadas assim que o segundo jogador entra
        enviar(cliente, "\nJogo iniciado!")
        enviar(cliente, "\nEscolha: pedra, papel ou tesoura")
        enviar(cliente, "\nDigite 'sair' para sair.\n")
        
        # Loop principal da partida
        while True:
            # Recebe dados do cliente de até 1024 bytes
            data = cliente.recv(1024)
            
            # Se o cliente desconectar (não houver dados recebidos)
            if not data:
                break
                
            # decode() transforma bytes em string
            # strip() remove espaços extras e quebras de linha (\n)
            # lower() transforma todo o texto em minúsculo
            jogada = data.decode('utf-8').strip().lower()
            
            # Comando para encerrar a conexão
            if jogada == "sair":
                enviar(cliente, "Você saiu do jogo.")
                # Avisa o outro jogador sobre a saída do oponente
                for c in clientes:
                    if c != cliente:
                        enviar(c, "\nO outro jogador saiu.")
                        enviar(c, "Partida encerrada.")
                break
                
            # Validação da jogada informada
            if jogada not in opcoes:
                enviar(cliente, "Jogada inválida.")
                continue
                
            # Lock protege o dicionário de jogadas, evitando Condição de Corrida (Race Condition)
            with lock:
                # Salva a jogada utilizando o número de identificação do jogador
                jogadas[numero_jogador] = jogada
                
            enviar(cliente, "\nEsperando oponente...\n")
            
            # Primeira Barreira: espera os dois jogadores realizarem suas jogadas
            barreira.wait()
            
            # Apenas o jogador 1 processa o resultado para evitar duplicação no envio
            if numero_jogador == 1:
                with lock:
                    # Recupera as jogadas salvas no dicionário
                    j1 = jogadas[1]
                    j2 = jogadas[2]
                    
                    # Calcula o vencedor da rodada
                    vencedor = determinar_vencedor(j1, j2)
                    
                    # Caso de empate
                    if vencedor == "empate":
                        msg1 = f"""
====================
RESULTADO
====================

Você jogou: {j1.upper()}
Oponente jogou: {j2.upper()}

EMPATE
"""
                        msg2 = msg1
                        
                    # Caso o jogador 1 vença
                    elif vencedor == "jogador1":
                        msg1 = f"""
====================
RESULTADO
====================

Você jogou: {j1.upper()}
Oponente jogou: {j2.upper()}

VOCÊ VENCEU
"""
                        msg2 = f"""
====================
RESULTADO
====================

Você jogou: {j2.upper()}
Oponente jogou: {j1.upper()}

VOCÊ PERDEU
"""
                    # Caso o jogador 2 vença
                    else:
                        msg1 = f"""
====================
RESULTADO
====================

Você jogou: {j1.upper()}
Oponente jogou: {j2.upper()}

VOCÊ PERDEU
"""
                        msg2 = f"""
====================
RESULTADO
====================

Você jogou: {j2.upper()}
Oponente jogou: {j1.upper()}

VOCÊ VENCEU
"""

                    # Envia o resultado estruturado para ambos os clientes
                    enviar(clientes[0], msg1)
                    enviar(clientes[1], msg2)
                    
                    # Limpa o dicionário para a próxima rodada
                    jogadas.clear()
                    
                    # Notifica o início de um novo turno
                    enviar(clientes[0], "\nNova rodada!")
                    enviar(clientes[1], "\nNova rodada!")
                    
            # Segunda Barreira: garante que ambas as threads concluam a rodada atual
            # antes de permitirem a leitura de novas jogadas no início do loop.
            barreira.wait()
            
    # Caso ocorra alguma desconexão inesperada do cliente
    except:
        print(f"Jogador {numero_jogador} desconectou.")
    finally:
        # Garante o fechamento do socket do cliente
        cliente.close()
        # Remove o cliente da lista ativa do servidor
        if cliente in clientes:
            clientes.remove(cliente)

# Instancia o socket principal utilizando IPv4 (AF_INET) e TCP (SOCK_STREAM)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
    # bind() associa o IP e a porta configurados ao socket do servidor
    servidor.bind((HOST, PORT))
    
    # Coloca o socket em modo de escuta passiva para conexões
    servidor.listen()
    print(f"\nServidor iniciado na porta {PORT}")
    print("Aguardando jogadores...\n")
    
    # Aceita conexões até atingir o limite estipulado de dois jogadores
    while len(clientes) < 2:
        # accept() bloqueia o fluxo e aceita a conexão TCP de entrada
        conn, addr = servidor.accept()
        
        # Adiciona a conexão do cliente à lista
        clientes.append(conn)
        
        # Define o número de identificação do jogador com base no tamanho da lista
        numero_jogador = len(clientes)
        print(f"Jogador {numero_jogador} conectado: {addr}")
        
        # Cria uma thread individual dedicada para gerenciar o respectivo cliente
        thread = threading.Thread(
            target=gerenciar_cliente,
            args=(conn, numero_jogador)
        )
        # Inicia a execução da thread em paralelo
        thread.start()
        
    print("\nDois jogadores conectados.")
    print("Partida iniciada.\n")
