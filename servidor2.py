import socket
import threading

HOST = "10.149.148.55"
PORT = 4000

clientes = []
jogadas = {}

lock = threading.Lock()

# BARRIER:
# só continua quando 2 jogadores chegarem nela
barreira = threading.Barrier(2)

opcoes = ['pedra', 'papel', 'tesoura']


# =========================
# DEFINIR VENCEDOR
# =========================

def determinar_vencedor(j1, j2):

    if j1 == j2:
        return "empate"

    elif (j1 == 'pedra' and j2 == 'tesoura') or \
         (j1 == 'papel' and j2 == 'pedra') or \
         (j1 == 'tesoura' and j2 == 'papel'):

        return "jogador1"

    else:
        return "jogador2"


# =========================
# ENVIAR MENSAGEM
# =========================

def enviar(cliente, mensagem):

    cliente.sendall(mensagem.encode('utf-8'))


# =========================
# THREAD CLIENTE
# =========================

def gerenciar_cliente(cliente, numero_jogador):

    global jogadas

    try:

        # =========================
        # ESPERA SEGUNDO JOGADOR
        # =========================

        if len(clientes) < 2:
            enviar(cliente, "Esperando outro jogador...\n")

        while len(clientes) < 2:
            pass

        enviar(cliente, "\nJogo iniciado!")
        enviar(cliente, "\nEscolha: pedra, papel ou tesoura")
        enviar(cliente, "\nDigite 'sair' para sair.\n")

        # =========================
        # LOOP DO JOGO
        # =========================

        while True:

            data = cliente.recv(1024)

            if not data:
                break

            jogada = data.decode('utf-8').strip().lower()

            # =========================
            # SAIR
            # =========================

            if jogada == "sair":

                enviar(cliente, "Você saiu do jogo.")

                for c in clientes:
                    if c != cliente:
                        enviar(c, "\nO outro jogador saiu.")

                break

            # =========================
            # VALIDAÇÃO
            # =========================

            if jogada not in opcoes:

                enviar(cliente, "Jogada inválida.")
                continue

            # =========================
            # SALVA JOGADA
            # =========================

            with lock:

                jogadas[numero_jogador] = jogada

            enviar(cliente, "\nEsperando oponente...\n")

            # =========================
            # ESPERA AMBOS JOGAREM
            # =========================

            barreira.wait()

            # =========================
            # APENAS UMA THREAD
            # PROCESSA RESULTADO
            # =========================

            if numero_jogador == 1:

                with lock:

                    j1 = jogadas[1]
                    j2 = jogadas[2]

                    vencedor = determinar_vencedor(j1, j2)

                    # =========================
                    # EMPATE
                    # =========================

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

                    # =========================
                    # JOGADOR 1 VENCEU
                    # =========================

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

                    # =========================
                    # JOGADOR 2 VENCEU
                    # =========================

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

                    # =========================
                    # ENVIA RESULTADO
                    # =========================

                    enviar(clientes[0], msg1)
                    enviar(clientes[1], msg2)

                    # =========================
                    # LIMPA JOGADAS
                    # =========================

                    jogadas.clear()

                    enviar(clientes[0], "\nNova rodada!")
                    enviar(clientes[1], "\nNova rodada!")

            # =========================
            # ESPERA LIMPEZA TERMINAR
            # =========================

            barreira.wait()

    except:

        print(f"Jogador {numero_jogador} desconectou.")

    finally:

        cliente.close()

        if cliente in clientes:
            clientes.remove(cliente)


# =========================
# SERVIDOR PRINCIPAL
# =========================

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:

    servidor.bind((HOST, PORT))

    servidor.listen()

    print(f"\nServidor iniciado na porta {PORT}")
    print("Aguardando jogadores...\n")

    # =========================
    # CONECTA 2 CLIENTES
    # =========================

    while len(clientes) < 2:

        conn, addr = servidor.accept()

        clientes.append(conn)

        numero_jogador = len(clientes)

        print(f"Jogador {numero_jogador} conectado: {addr}")

        thread = threading.Thread(
            target=gerenciar_cliente,
            args=(conn, numero_jogador)
        )

        thread.start()

    print("\nDois jogadores conectados.")
    print("Partida iniciada.\n")
