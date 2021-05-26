#!/usr/bin/python3

import sys
import socket
import select
import csv
import random
from common_comm import send_dict, recv_dict, sendrecv_dict
import os

# from Crypto.Cipher import AES

# Dicionário com a informação relativa aos clientes
gammers = {}


# return the client_id of a socket or None
def find_client_id(client_sock):
    for client_id in gammers.keys():  # percorre o array das chaves do dicionário gammers
        if gammers[client_id]['socket'] == client_sock:  # se o socket for igual ao que queremos, retornamos o id
            return client_id
    return None


#
# Incomming message structure:
# { op = "START", client_id}
# { op = "QUIT" }
# { op = "GUESS", number }
# { op = "STOP", number, attempts }
#
# Outcomming message structure:
# { op = "START", status, max_attempts }
# { op = "QUIT" , status }
# { op = "GUESS", status, result }
# { op = "STOP", status, guess }


#
# Suporte de desnw
# codificação da operação pretendida pelo cliente
#
def new_msg(client_sock):
    in_msg = recv_dict(client_sock)
    print(in_msg)
    ##validate_msg(in_msg)
    if in_msg['op'] == "START":
        out_msg = new_client(client_sock, in_msg)

    elif in_msg['op'] == "QUIT":
        out_msg = quit_client(client_sock, in_msg)

    elif in_msg['op'] == "GUESS":
        out_msg = guess_client(client_sock, in_msg)

    else:  # in_msg['op'] == "STOP"
        out_msg = stop_client(client_sock, in_msg)

    print(out_msg)
    send_dict(client_sock, out_msg)

    return None


# read the client request
# detect the operation requested by the client
# execute the operation and obtain the response (consider also operations not available)
# send the response to the client


#
# Suporte da criação de um novo jogador - operação START
#
def new_client(client_sock, request):
    # detect the client in the request
    client_id = request['client_id']

    # verify the appropriate conditions for executing this operation
    if not (client_id in gammers):  # se o programa não achar o cliente na lista de gammers, é um clente novo

        # obtain the secret number and number of attempts
        secret_number = random.randint(0, 100)
        max_attempts = random.randint(10, 30)

        # for debug
        ##secret_number = 5
        ##max_attempts = 3

        # process the client in the dictionary
        gammers[client_id] = {}
        gammers[client_id]['socket'] = client_sock
        gammers[client_id]['guess'] = secret_number
        gammers[client_id]['max_attempts'] = max_attempts
        gammers[client_id]['attempts'] = 0
        ##print(gammers)

        out_msg = {"op": "START", "status": True, "max_attempts": max_attempts}
    else:  # estamos diante de uma operação inválida
        out_msg = {"op": "START", "status": False, "error": "Cliente existente"}

    # return response message with results or error message
    return out_msg


#
# Suporte da eliminação de um cliente
#
def clean_client(client_sock):
    client_id = find_client_id(client_sock)
    if client_id != None:
        gammers.pop(client_id)  # remove o usuário do dict gammers
    return None


# obtain the client_id from his socket and delete from the dictionary


#
# Suporte do pedido de desistência de um cliente - operação QUIT
#
def quit_client(client_sock, request):
    # obtain the client_id from his socket
    client_id = find_client_id(client_sock)

    # verify the appropriate conditions for executing this operation
    if client_id != None:  # se o programa achar o cliente na lista de gammers

        # process the report file with the QUIT result
        update_file(client_id, "QUIT")

        # eliminate client from dictionary
        clean_client(client_sock)
        ##print(gammers)

        out_msg = {"op": "QUIT", "status": True}
    else:  # estamos diante de uma operação inválida
        out_msg = {"op": "QUIT", "status": False, "error": "Cliente inexistente"}

    # return response message with results or error message
    return out_msg


#
# Suporte da criação de um ficheiro csv com o respectivo cabeçalho
#
def create_file():
    if not os.path.exists('report.csv'):
        fout = open('report.csv', 'w')  # abre em modo writer
        writer = csv.DictWriter(fout, fieldnames=['user_id', 'secret_number', 'maximum', 'n_plays', 'resultado'])
        writer.writeheader()  # escreve o cabeçalho
        fout.close()
    return None


# create report csv file with header


#
# Suporte da actualização de um ficheiro csv com a informação do cliente e resultado
#
def update_file(client_id, result):
    fout = open('report.csv', 'a')  # abre o report.csv em modo append
    writer = csv.DictWriter(fout, fieldnames=['user_id', 'secret_number', 'maximum', 'n_plays', 'resultado'])
    data = {}
    data['user_id'] = client_id
    data['secret_number'] = gammers[client_id]['guess']
    data['maximum'] = gammers[client_id]['max_attempts']
    data['n_plays'] = gammers[client_id]['attempts']
    data['resultado'] = result  # update report csv file with the result from the client
    writer.writerow(data)
    fout.close()
    return None


# update report csv file with the result from the client


#
# Suporte da jogada de um cliente - operação GUESS
#
def guess_client(client_sock, request):
    # obtain the client_id from his socket
    client_id = find_client_id(client_sock)

    # verify the appropriate conditions for executing this operation
    if client_id != None:  # se o programa achar o cliente na lista de gammers

        # compara o valor indicado pelo cliente com o número secreto
        if request["number"] < gammers[client_id]["guess"]:
            result = "larger"  # se for menor, envia para o cliente que a próxima deve ser maior
        elif request["number"] > gammers[client_id]["guess"]:
            result = "smaller"
        else:
            result = "equals"

        gammers[client_id]["attempts"] += 1  # update o número de tentativas

        out_msg = {"op": "GUESS", "status": True, "result": result}
    else:  # estamos diante de uma operação inválida
        out_msg = {'op': 'GUESS', 'status': False}

    # return response message with results or error message
    return out_msg


#
# Suporte do pedido de terminação de um cliente - operação STOP
#
def stop_client(client_sock, request):
    # o request será do tipo -> { op = "STOP", number, attempts }
    client_id = find_client_id(client_sock)  # obtain the client_id from his socket
    gammers[client_id]["attempts"] += 1  # a ultima jogada tambem conta como jogada

    if client_id != None:  # verify the appropriate conditions for executing this operation

        print((gammers[client_id]["attempts"], request["attempts"],
               gammers[client_id]["attempts"] == request["attempts"]))
        if gammers[client_id]["attempts"] == request["attempts"]:  # se o numero de tenteativas for consistente

            print((request["number"], gammers[client_id]["guess"], request["number"] == gammers[client_id]["guess"]))
            result = "SUCCESS" if request["number"] == gammers[client_id][
                "guess"] else "FAILURE"  # se o jogador acertou
            out_msg = {"op": "STOP", "status": True, "guess": gammers[client_id]["guess"]}

            update_file(client_id, result)  # process the report file with the SUCCESS/FAILURE result
            clean_client(client_sock)  # eliminate client from dictionary

        else:
            out_msg = {"op": "STOP", "status": False, "error": "Número de jogadas inconsistente"}
    else:
        out_msg = {"op": "STOP", "status": False, "error": "Cliente inexistente"}

    return out_msg  # return response message with result or error message


# validate the number of arguments and eventually print error message and exit with error
# verify type of of arguments and eventually print error message and exit with error
def validate_call():
    if len(sys.argv) != 2:
        print("insuficiencia ou excesso de argumentos passados")
        exit(1)

    # valor inteiro positivo, especificando o porto TCP do servidor;
    # aceita qualquer porto de 4 digitos
    if sys.argv[1].isnumeric():
        port = int(sys.argv[1])
        if port < 1000 or port > 9999:
            print("porto invalido")
            exit(2)
    else:
        print("tipo errado")
        exit(2)

    return int(sys.argv[1])


def main():
    port = validate_call()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen(10)

    clients = []

    create_file()

    while True:
        try:
            available = select.select([server_socket] + clients, [], [])[0]
        except ValueError:
            # Sockets may have been closed, check for that
            for client_sock in clients:
                if client_sock.fileno() == -1: clients.remove(client_sock)  # closed
            continue  # Reiterate select

        for client_sock in available:
            # New client?
            if client_sock is server_socket:
                newclient, addr = server_socket.accept()
                clients.append(newclient)
            # Or an existing client
            else:
                # See if client sent a message
                if len(client_sock.recv(1, socket.MSG_PEEK)) != 0:
                    # client socket has a message
                    ##print ("server" + str (client_sock))
                    new_msg(client_sock)
                else:  # Or just disconnected
                    clients.remove(client_sock)
                    clean_client(client_sock)
                    client_sock.close()
                    break  # Reiterate select


if __name__ == "__main__":
    main()
