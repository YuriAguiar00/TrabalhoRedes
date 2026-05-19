import socket
import random

HOST = "127.0.0.1"
PORT = 4000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((HOST, PORT))
        print("Conectado ao servidor.")

        while True:
            print("Escolha uma das opções a seguir para realizar sua jogada")
            print("Pedra, Papel ou Tesoura")
            print("Digite 'Sair' se deseja encerrar a conexão.")
            jogada = input(">> ")

            if jogada ==  "sair":
                print("A conexão com o servidor foi encerrada.")
                break

            if jogada not in ['pedra', 'papel', 'tesoura']:
                print("Opção inválida. Certifique-se usar apenas os comandos apresentados anteriormente.")
                continue

            s.sendall(jogada.encode('utf-8'))
            data = s.recv(1024)
            print(f">> {data.decode('utf-8')}")


    except ConnectionRefusedError:
        print("Falha na conexão.")
