import socket
import threading
import os
import json

class Servidor:
    def __init__(self, host='localhost', port=0, gerenciador_host='localhost', gerenciador_port=5000):
        self.host = host
        self.port = port
        self.gerenciador_host = gerenciador_host
        self.gerenciador_port = gerenciador_port

    def iniciar(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        self.port = server_socket.getsockname()[1]
        server_socket.listen(5)
        print(f"Servidor iniciado no endereço {self.host}:{self.port}")

        self.registrar_com_gerenciador()

        while True:
            client_socket, client_address = server_socket.accept()
            threading.Thread(target=self.tratar_cliente, args=(client_socket,)).start()

    def registrar_com_gerenciador(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.gerenciador_host, self.gerenciador_port))
            mensagem = {
                'tipo': 'registro',
                'host': self.host,
                'port': self.port
            }
            self.enviar_mensagem(s, mensagem)
            resposta = self.receber_mensagem(s)
            print(f"Resposta do gerenciador: {resposta}")
        except Exception as e:
            print(f"Erro ao registrar com o gerenciador: {e}")
        finally:
            s.close()

    def tratar_cliente(self, client_socket):
        try:
            tipo_mensagem = self.receber_dados(client_socket).decode('utf-8')
            mensagem = json.loads(tipo_mensagem)
            print(f"Mensagem recebida do cliente: {mensagem}")

            if mensagem['tipo'] == 'backup':
                nome_arquivo = mensagem['arquivo']
                conteudo = self.receber_dados(client_socket)

                diretorio = "C:\\UFABC\\Sitemas Distribuidos\\Backup"
                os.makedirs(diretorio, exist_ok=True)
                caminho_arquivo = os.path.join(diretorio, nome_arquivo)

                with open(caminho_arquivo, 'wb') as f:
                    f.write(conteudo)

                print(f"Arquivo {nome_arquivo} recebido e armazenado.")
            else:
                print("Tipo de mensagem desconhecido.")
        except Exception as e:
            print(f"Erro ao tratar cliente: {e}")
        finally:
            client_socket.close()

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

    def receber_mensagem(self, client_socket):
        dados = self.receber_dados(client_socket)
        return json.loads(dados.decode('utf-8'))

if __name__ == '__main__':
    servidor = Servidor()
    servidor.iniciar()
