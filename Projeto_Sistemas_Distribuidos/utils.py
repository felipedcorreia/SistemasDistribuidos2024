import json
import socket

def enviar_mensagem(sock, mensagem):
    mensagem_json = json.dumps(mensagem)
    sock.sendall(mensagem_json.encode('utf-8'))

def receber_mensagem(sock):
    dados = sock.recv(1024)
    return json.loads(dados.decode('utf-8'))