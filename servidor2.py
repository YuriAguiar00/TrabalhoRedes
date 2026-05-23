import socket # biblioteca responsável pela comunicação em rede
import threading # permite múltiplas tarefas simultâneas
HOST = "10.149.148.55" # IP do servidor
PORT = 4000 # porta da aplicação
clientes = [] # lista que guarda os sockets dos jogadores o conn dos usua´rios cada elemento é um socket tco, conexão com redes
jogadas = {} # armazena as jogadas da rodada atual
# lock impede que duas threads alterem dados ao mesmo tempo
lock = threading.Lock()
# barrier sincroniza os dois jogadores
# só continua quando os dois chegarem nela (tratamento de erro de desicronização)
barreira = threading.Barrier(2)
# jogadas válidas
opcoes = ['pedra', 'papel', 'tesoura']
# função responsável por definir vencedor
def determinar_vencedor(j1, j2):
    # caso empate
    if j1 == j2:
        return "empate"
    # regras de vitória do jogador 1
    elif (j1 == 'pedra' and j2 == 'tesoura') or \
         (j1 == 'papel' and j2 == 'pedra') or \
         (j1 == 'tesoura' and j2 == 'papel'):
        return "jogador1"
    # inverso, jogador 2 vence
    else:
        return "jogador2"
# função para enviar mensagens para clientes
def enviar(cliente, mensagem):
    # encode transforma string em bytes
    # sendall garante envio completo
    cliente.sendall(mensagem.encode('utf-8'))
 # função principal de cada jogador
 # cada cliente conectado ganha uma thread
def gerenciar_cliente(cliente, numero_jogador):
    global jogadas
    try:
        # se ainda não houver dois jogadores
        if len(clientes) < 2:
            enviar(cliente, "Esperando outro jogador...\n")
        # espera até o segundo jogador entrar
        while len(clientes) < 2:
            pass
        # mensagens iniciais (quando segundo jogador entra, coonversa com o len de cima)
        enviar(cliente, "\nJogo iniciado!")
        enviar(cliente, "\nEscolha: pedra, papel ou tesoura")
        enviar(cliente, "\nDigite 'sair' para sair.\n")
        # loop principal da partida
        while True:
            # recebe dados do cliente de até 1024 bytes
            data = cliente.recv(1024)
            # se cliente desconectar (não houver dado)
            if not data:
                break
            # decode transforma bytes em string
            # strip remove espaços/quebras de linha
            # lower transforma tudo em minúsculo
            jogada = data.decode('utf-8').strip().lower()
            # comando sair
            if jogada == "sair":
                enviar(cliente, "Você saiu do jogo.")
                # avisa outro jogador da saída
                for c in clientes:
                    if c != cliente:
                        enviar(c, "\nO outro jogador saiu.")
                break
            # validação da jogada
            if jogada not in opcoes:
                enviar(cliente, "Jogada inválida.")
                continue
            # lock protege o dicionário jogada evitando race condition (tratamentod e erro)
            with lock:
                # salva jogada do jogador (no número do jogador na lista)
                jogadas[numero_jogador] = jogada
            enviar(cliente, "\nEsperando oponente...\n")
            # barrier:
            # espera os dois jogadores jogarem
            barreira.wait()
            # apenas jogador 1 processa resultado para que não haja duplicação
            if numero_jogador == 1:
                with lock:
                    # pega jogadas salvas
                    j1 = jogadas[1]
                    j2 = jogadas[2]
                    # calcula vencedor
                    vencedor = determinar_vencedor(j1, j2)
                    #caso de empate
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
                    # jogador 1 venceu
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
                    # jogador 2 venceu
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

                    # envia resultado para ambos
                    enviar(clientes[0], msg1)
                    enviar(clientes[1], msg2)
                    # limpa jogadas da rodada
                    jogadas.clear()
                    # avisa nova rodada
                    enviar(clientes[0], "\nNova rodada!")
                    enviar(clientes[1], "\nNova rodada!")
            # segunda barrier, garante que ambas thread terminem antes da próxima rodada
            barreira.wait()
    # caso cliente desconecte
    except:
        print(f"Jogador {numero_jogador} desconectou.")
    finally:
        # fecha socket
        cliente.close()
        # remove cliente da lista
        if cliente in clientes:
            clientes.remove(cliente)
# cria socket TCP IPv4
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
    # bind associa IP e porta ao socket
    servidor.bind((HOST, PORT))
    # coloca socket em modo escuta
    servidor.listen()
    print(f"\nServidor iniciado na porta {PORT}")
    print("Aguardando jogadores...\n")
    # aceita apenas dois jogadores
    while len(clientes) < 2:
        # accept aceita conexão TCP
        conn, addr = servidor.accept()
        # salva cliente conectado
        clientes.append(conn)
        # define número do jogador
        numero_jogador = len(clientes)
        print(f"Jogador {numero_jogador} conectado: {addr}")
        # cria thread individual para cliente
        thread = threading.Thread(
            target=gerenciar_cliente,
            args=(conn, numero_jogador)
        )
        # inicia thread
        thread.start()
    print("\nDois jogadores conectados.")
    print("Partida iniciada.\n")
