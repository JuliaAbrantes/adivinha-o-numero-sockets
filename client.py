#!/usr/bin/python3

import sys
import socket
from common_comm import send_dict, recv_dict, sendrecv_dict


# verify if response from server is valid or is an error message and act accordingly
def validate_response(client_sock, in_msg):
    if in_msg == None:
        print("nao foi possivel enviar a requisicao ou receber a reposta")
        client_sock.close()  # fecha o socket
        exit(3)  # sai com código 3

    if not in_msg["status"]:  # se a operação não foi bem sucedida
        try:
            print(in_msg["error"])  # exibe o erro se tiver
        except:
            print("o servidor retornou um erro")  # exibe um erro genérico
        client_sock.close()  # fecha o socket
        exit(3)  # sai com código 3


# process QUIT operation
def quit_action(client_sock, attempts):
    out_msg = {"op": "QUIT"}  # assemble the message QUIT
    print(out_msg)
    in_msg = sendrecv_dict(client_sock, out_msg)  # send the message
    print(in_msg)

    validate_response(client_sock, in_msg)
    print("o jogo terminou com sucesso")
    exit(4)


# Outcomming message structure:
# { op = "START", client_id, [cipher] }
# { op = "QUIT" }
# { op = "GUESS", number }
# { op = "STOP", number, attempts }
#
# Incomming message structure:
# { op = "START", status, max_attempts }
# { op = "QUIT" , status }
# { op = "GUESS", status, result }
# { op = "STOP", status, guess }

# auxiliar function to get a valid user input
def get_input():
    # asks for the next guess until its a integer
    while True:
        inp = input("make your guess: ")
        if inp.isnumeric():  # se o input for um número inteiro positivo sem espaços
            return int(inp)  # retornamos True porque o retorno é um nomero válido
        else:
            if inp.upper() == "QUIT":  # testa se é a string "quit"
                print("vamos processar a desistencia")
                return "QUIT"  # retornamos False porque o retorno não é um numero válido
            else:
                print("Um numero inteiro Caracas")


# process START operation
def start_client(client_sock, client_id):
    out_msg = {"op": "START", "client_id": client_id}  # sends the start message
    print(out_msg)
    in_msg = sendrecv_dict(client_sock, out_msg)
    print(in_msg)

    validate_response(client_sock, in_msg)
    return in_msg["max_attempts"]


def guess_action(client_sock, attempts, number):
    out_msg = {"op": "GUESS", "number": number}  # assemble the message
    print(out_msg)
    in_msg = sendrecv_dict(client_sock, out_msg)  # send the message
    print(in_msg)

    validate_response(client_sock, in_msg)
    print(in_msg["result"])  # imprime se a adivinha foi maior menor ou igual

    if in_msg["result"] == "equals":  # se foi igual, temos que parar o jogo
        stop_action(client_sock, attempts, number)

    return None


# cria, envia, recebe e processa o pedido de STOP
def stop_action(client_sock, n_plays, number):
    out_msg = {"op": "STOP", "number": number, "attempts": n_plays}  # assemble the message STOP
    print(out_msg)
    in_msg = sendrecv_dict(client_sock, out_msg)  # send the message
    print(in_msg)
    validate_response(client_sock, in_msg)

    # exibe mensagem de vitória ou derrota
    if in_msg["guess"] == number:
        print("YOU WON XD")
    else:
        print("YOU LOST T-T")
        print("o numero era: " + str(in_msg["guess"]))
    exit(0)  # o programa terminou normalmente


#
# Suporte da execução do cliente
#
def run_client(client_sock, client_id):
    max_plays = start_client(client_sock, client_id)  # inicializar as variáveis para contar as jogadas
    n_plays = 0

    while True:
        input = get_input()
        if input == "QUIT":  # se o jogador quiser desistir
            quit_action(client_sock, n_plays)
            break
        else:
            n_plays += 1
            if n_plays < max_plays:  # se o jogador ainda tiver jogadas para fazer
                guess_action(client_sock, n_plays, input)
            else:  # se chegar ao limite de jogadas, esta será a última jogada
                stop_action(client_sock, n_plays, input)

    return None


# validate the number of arguments and eventually print error message and exit with error
# verify type of of arguments and eventually print error message and exit with error
def validate_call():
    if len(sys.argv) != 4 and len(sys.argv) != 3:
        print("insuficiencia ou excesso de argumentos passados")
        exit(1)
    # 2. O segundo argumento é o identificador pessoal do cliente que pretende aceder ao servidor para jogar;
    # qualquer string é válida, por isso não há testes a fazer

    # 3. O terceiro argumento deverá ser um valor inteiro positivo, especificando o porto TCP do servidor;
    # aceita qualquer porto de 4 digitos
    if sys.argv[2].isnumeric():
        port = int(sys.argv[2])
        if port < 1000 or port > 9999:
            print("porto invalido")
            exit(2)
    else:
        print("tipo errado")
        exit(2)

    return None


def main():
    validate_call()

    client_id = sys.argv[1]
    port = int(sys.argv[2])

    # 4. O quarto argumento devera ser um nome DNS ou endereço IPv4 no formato
    # X.X.X.X, onde X representa um valor inteiro decimal entre 0 e 255.
    # Se este argumento não for indicado, o cliente devera usar um servidor na mesma maquina
    # onde esta (localhost);
    hostname = sys.argv[3] if len(sys.argv) == 4 else "127.0.0.1"

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((hostname, port))  # tenta conectar ao servidor
    except:
        print("dificuldades ao conectar com o servidor")
        exit(2)

    print("client runing")
    # quit_action(client_sock,3)
    # guess_action(client_sock,3,5)
    # stop_action(client_sock,3,5)
    run_client(client_sock, client_id)
    client_sock.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
