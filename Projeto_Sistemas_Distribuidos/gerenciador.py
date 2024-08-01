import socket
import threading
import json

class Gerenciador:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.servidores = []

    def iniciar(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Gerenciador iniciado no endereço {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=self.tratar_cliente, args=(client_socket,)).start()

    def tratar_cliente(self, client_socket):
        try:
            dados = self.receber_dados(client_socket)
            mensagem = json.loads(dados.decode('utf-8'))
            print(f"Mensagem recebida do cliente: {mensagem}")

            if mensagem['tipo'] == 'registro':
                self.registrar_servidor(mensagem)
            elif mensagem['tipo'] == 'backup':
                self.escolher_servidores(client_socket, mensagem['arquivo'])
            else:
                print("Tipo de mensagem desconhecido.")
        except Exception as e:
            print(f"Erro ao tratar cliente: {e}")
        finally:
            client_socket.close()

    def registrar_servidor(self, mensagem):
        try:
            servidor = (mensagem['host'], mensagem['port'])
            self.servidores.append(servidor)
            print(f"Servidor registrado: {servidor}")
        except Exception as e:
            print(f"Erro ao registrar servidor: {e}")

    def escolher_servidores(self, client_socket, arquivo):
        if len(self.servidores) < 2:
            self.enviar_mensagem(client_socket, {'erro': 'Não há servidores suficientes para escolher.'})
            return

        import random
        servidor_principal = random.choice(self.servidores)
        servidor_replicado = random.choice([srv for srv in self.servidores if srv != servidor_principal])
        
        resposta = {
            'servidor_principal': servidor_principal,
            'servidor_replicado': servidor_replicado
        }

        self.enviar_mensagem(client_socket, resposta)

    def receber_dados(self, client_socket, buffer_size=4096):
        dados = b''
        while True:
            parte = client_socket.recv(buffer_size)
            if not parte:
                break
            dados += parte
        return dados

    def enviar_mensagem(self, client_socket, mensagem):
        mensagem_json = json.dumps(mensagem)
        client_socket.sendall(mensagem_json.encode('utf-8'))

if __name__ == '__main__':
    gerenciador = Gerenciador()
    gerenciador.iniciar()
