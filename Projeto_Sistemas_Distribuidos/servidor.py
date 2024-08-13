import socket
import threading
import json
import os
import base64

class Servidor:
    def __init__(self, host='localhost', port=59001, gerenciador_host='localhost', gerenciador_port=5000):
        self.host = host
        self.port = port
        self.gerenciador_host = gerenciador_host
        self.gerenciador_port = gerenciador_port
        self.diretorio_backup = r"C:\Backup1"
        self.diretorio_backup_replicado = r"C:\Backup2"

    def iniciar(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(5)
        print(f"Servidor iniciado no endereço {self.host}:{self.port}")

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
            mensagem = json.loads(dados.decode('utf-8'))
            print(f"Mensagem recebida do cliente: {mensagem}")

            if isinstance(mensagem, dict):
                if mensagem['tipo'] == 'backup':
                    print(f"Tratando backup para o arquivo: {mensagem['arquivo']}")
                    conteudo_decodificado = base64.b64decode(mensagem['conteudo'])
                    self.salvar_arquivo(mensagem['arquivo'], conteudo_decodificado)
                else:
                    print(f"Tipo de mensagem desconhecido: {mensagem['tipo']}")
            else:
                print(f"Erro: A mensagem não é um dicionário, mas sim {type(mensagem)}.")
        except Exception as e:
            print(f"Erro ao tratar cliente: {e}")

    def salvar_arquivo(self, nome_arquivo, conteudo):
        try:
            # Salva no diretório de backup principal
            caminho_backup = os.path.join(self.diretorio_backup, nome_arquivo)
            with open(caminho_backup, 'wb') as f:
                f.write(conteudo)
            print(f"Arquivo {nome_arquivo} salvo em {self.diretorio_backup}")

            # Salva no diretório de backup replicado
            caminho_replicado = os.path.join(self.diretorio_backup_replicado, nome_arquivo)
            with open(caminho_replicado, 'wb') as f:
                f.write(conteudo)
            print(f"Arquivo {nome_arquivo} salvo em {self.diretorio_backup_replicado}")

        except Exception as e:
            print(f"Erro ao salvar arquivo {nome_arquivo}: {e}")

    def receber_dados(self, client_socket):
        tamanho_conteudo = int.from_bytes(client_socket.recv(8), 'big')
        dados = b''
        while len(dados) < tamanho_conteudo:
            parte = client_socket.recv(4096)
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
