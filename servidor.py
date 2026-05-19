import socket
import random

HOST = "127.0.0.1"
PORT = 4000

opcoes = ['pedra', 'papel', 'tesoura']

def determinar_vencedor(jogada_cliente, jogada_servidor):
    if jogada_cliente == jogada_servidor:
        return "Empate."

    elif (jogada_cliente == 'pedra' and jogada_servidor == 'tesoura') or \
         (jogada_cliente == 'papel' and jogada_servidor == 'pedra') or \
         (jogada_cliente == 'tesoura' and jogada_servidor == 'papel'):
         return "Você venceu."

    else:
        return "Você perdeu."

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Servidor iniciado. Aguardando cliente na porta {PORT}...")

    conn, addr = s.accept()
    with conn:
        print(f"Conexão estabelecida com {addr}")

        while True:
            data = conn.recv(1024)

            if not data:
                print("Cliente desconectou.")
                break

            jogada_cliente = data.decode('utf-8').lower()

            if jogada_cliente not in opcoes:
                erro = "Jogada inválida. Tente uma das opções disponíveis"
                conn.sendall(erro.encode('utf-8'))
                continue

            jogada_servidor = random.choice(opcoes)
            resultado = determinar_vencedor(jogada_cliente, jogada_servidor)

            resposta = f"Servidor escolheu {jogada_servidor.upper()}. {resultado}"
            conn.sendall(resposta.encode('utf-8'))
