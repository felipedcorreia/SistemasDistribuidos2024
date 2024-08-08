import socket
import threading
import json
import os

class Servidor:
    def __init__(self, host='localhost', port=59001, gerenciador_host='localhost', gerenciador_port=5000):
        self.host = host
        self.port = port
        self.gerenciador_host = gerenciador_host
        self.gerenciador_port = gerenciador_port
        self.diretorio_backup = r"C:\UFABC\Sitemas Distribuidos\Backup" 

    def iniciar(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        print(f"Servidor iniciado no endereço {self.host}:{self.port}")

        # Registrar servidor no gerenciador
        self.registrar_servidor()

        while True:
            client_socket, client_address = s.accept()
            print(f"Conexão com cliente estabelecida de {client_address}")
            threading.Thread(target=self.tratar_cliente, args=(client_socket,)).start()

    def registrar_servidor(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.gerenciador_host, self.gerenciador_port))

            mensagem = {
                'tipo': 'registro',
                'host': self.host,
                'port': self.port
            }
            self.enviar_mensagem(s, mensagem)
            print(f"Servidor registrado no gerenciador: {mensagem}")
        except Exception as e:
            print(f"Erro ao registrar servidor no gerenciador: {e}")

    def tratar_cliente(self, client_socket):
        try:
            dados = self.receber_dados(client_socket)
            print(f"Dados recebidos do cliente: {dados}")
            mensagem = json.loads(dados.decode('utf-8'))
            print(f"Mensagem recebida do cliente: {mensagem}")

            if mensagem['tipo'] == 'backup':
                self.salvar_arquivo(mensagem['arquivo'], mensagem['conteudo'])
        except Exception as e:
            print(f"Erro ao tratar cliente: {e}")
        finally:
            client_socket.close()

    def salvar_arquivo(self, nome_arquivo, conteudo):
        try:
            caminho_arquivo = os.path.join(self.diretorio_backup, nome_arquivo)
            with open(caminho_arquivo, 'wb') as f:
                f.write(conteudo)
            print(f"Arquivo {nome_arquivo} salvo com sucesso no diretório {self.diretorio_backup}.")
        except Exception as e:
            print(f"Erro ao salvar arquivo {nome_arquivo}: {e}")

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
        print(f"Mensagem enviada: {mensagem}")

if __name__ == '__main__':
    servidor1 = Servidor(port=59001)
    servidor2 = Servidor(port=59002)
    threading.Thread(target=servidor1.iniciar, name="Servidor1").start()
    threading.Thread(target=servidor2.iniciar, name="Servidor2").start()
