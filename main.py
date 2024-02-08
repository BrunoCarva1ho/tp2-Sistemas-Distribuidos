import time
import threading
import random
import socket
import os

def start(func):
    thread = threading.Thread(target=func)
    thread.start()

fila_espera = []
Recurso = False
eleicao_em_andamento = False
ip_address = None
eleito = None

def fila():
    global Recurso
    while True:
        if fila_espera:
            usuario = fila_espera.pop(0)
            print(f"O usuário {usuario} está usando o Recurso.")
            time.sleep(5)
            print(f"Usuário {usuario} liberou o Recurso ...\n\n")
            
            with open('log.txt', 'a') as arq:
                arq.write(f"\nO usuário {usuario} acessou o recurso.\n")
        else:
            Recurso = False
            print('O Recurso está desocupado ..')
            break


def comunica_usuario(ip_port):
    global Recurso
    global espera

    if not Recurso:
        print(f"Recurso liberado para o usuário {ip_port}.")
        start(fila)
        time.sleep(2)
        espera = 1
    elif espera == 1:
        print(f"Próximo da lista {fila_espera[0]}.")
        print(f"Fila de espera {fila_espera}.")
        espera = 2


def receive_connection():
    global ip_address
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(4)
    while True:
        client_socket, addr = server_socket.accept()
        ip_port = f"{addr[0]}:{addr[1]}"
        if not eleicao_em_andamento:
            if ip_address is None:
                ip_address = ip_port
                client_socket.send("leader".encode())
            else:
                client_socket.send("election".encode())
        else:
            client_socket.send("election".encode())

        fila_espera.append(ip_port)
        comunica_usuario(ip_port)


def simulate_access():
    global eleicao_em_andamento
    global eleito

    while True:
        if not Recurso:
            time.sleep(7)
            for _ in range(3):
                ip = f"192.168.1.{random.randint(1, 100)}"
                porta = random.randint(10000, 60000)
                ip_port = f"{ip}:{porta}"
                fila_espera.append(ip_port)
            comunica_usuario(fila_espera[0])
            espera = 1
        elif espera == 1:
            print(f"Próximo da lista {fila_espera[0]}.")
            print(f"Fila de espera {fila_espera}.")
            espera = 2

        if not eleicao_em_andamento:
            eleicao_em_andamento = True
            if ip_address == eleito or eleito is None:
                eleito = ip_address
                start(election)
            eleicao_em_andamento = False


def election():
    global eleicao_em_andamento
    global eleito

    print("Eleição requisitada ...")
    for dispositivo in fila_espera:
        ip, porta = dispositivo.split(":")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, int(porta)))
        mensagem = client_socket.recv(1024).decode()
        print(f"O lider agora é {dispositivo}")

        if mensagem == "election":
            if dispositivo == eleito:
                eleicao_em_andamento = False
                start(election)
            else:
                client_socket.send("election".encode())
        elif mensagem == "leader":
            eleicao_em_andamento = False
            eleito = dispositivo
            break

start(receive_connection)
simulate_access()
