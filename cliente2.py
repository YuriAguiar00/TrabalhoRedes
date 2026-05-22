import socket
import threading
# ip do roteador do yuri
HOST = "10.149.148.55"
PORT = 4000
# função de receber informações
def receber_mensagens(cliente):
    while True:
        try:
            mensagem = cliente.recv(1024).decode('utf-8')
            if not mensagem:
                break
            print(mensagem)

        except:
            break


# =========================
# CLIENTE PRINCIPAL
# =========================

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:

    try:

        cliente.connect((HOST, PORT))

        print("Conectado ao servidor.")

        # =========================
        # THREAD RECEBIMENTO
        # =========================

        thread = threading.Thread(
            target=receber_mensagens,
            args=(cliente,)
        )

        thread.daemon = True
        thread.start()

        # =========================
        # LOOP PRINCIPAL
        # =========================

        while True:

            jogada = input(">> ").strip().lower()

            # =========================
            # SAIR
            # =========================

            if jogada == "sair":

                cliente.sendall(jogada.encode('utf-8'))

                print("Você saiu do jogo.")

                break

            # =========================
            # VALIDAÇÃO
            # =========================

            if jogada not in ['pedra', 'papel', 'tesoura']:

                print("Jogada inválida.")
                print("Use: pedra, papel ou tesoura")

                continue

            # =========================
            # ENVIA AO SERVIDOR
            # =========================

            cliente.sendall(jogada.encode('utf-8'))

    except ConnectionRefusedError:

        print("Servidor não encontrado.")

    except:

        print("Erro na conexão.")
