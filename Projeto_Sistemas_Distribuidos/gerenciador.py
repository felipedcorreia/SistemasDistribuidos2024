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
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Conexão com cliente estabelecida de {client_address}")
                threading.Thread(target=self.tratar_cliente, args=(client_socket,)).start()
            except Exception as e:
                print(f"Erro ao aceitar conexão: {e}")

    def tratar_cliente(self, client_socket):
        dados = self.receber_dados(client_socket)
        if not dados:
            print("Nenhum dado recebido do cliente.")
            return

        print(f"Dados recebidos do cliente: {dados}")
        mensagem = json.loads(dados.decode('utf-8'))
        print(f"Mensagem decodificada: {mensagem}")

        if mensagem['tipo'] == 'registro':
            self.registrar_servidor(mensagem)
        elif mensagem['tipo'] == 'backup':
            if mensagem['conteudo'] is None:
                print("Aviso: O conteúdo do arquivo é None. Continuando com a escolha do servidor.")
            self.escolher_servidores(client_socket, mensagem['arquivo'])
        else:
            print("Tipo de mensagem desconhecido.")
        client_socket.close()
        print("Conexão com cliente encerrada.")


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
        print(f"Servidores escolhidos: {resposta}")

    def receber_dados(self, client_socket, buffer_size=4096):
        print(f"receber_dados")
        dados = b''
        # while True:
        parte = client_socket.recv(buffer_size)
          #   if not parte:
            #     break
        dados += parte
        print(f"Dados completos recebidos: {dados}")
        return dados

    def enviar_mensagem(self, client_socket, mensagem):
        try:
            mensagem_json = json.dumps(mensagem)
            client_socket.sendall(mensagem_json.encode('utf-8'))
            print(f"Mensagem enviada para o cliente: {mensagem_json}")
        except Exception as e:
            print(f"Erro ao enviar mensagem para o cliente: {e}")


if __name__ == '__main__':
    gerenciador = Gerenciador()
    gerenciador.iniciar()
