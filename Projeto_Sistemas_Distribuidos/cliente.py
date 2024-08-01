import socket
import json

class Cliente:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port

    def iniciar(self):
        nome_arquivo = input("Digite o nome do arquivo para backup: ")
        self.solicitar_backup(nome_arquivo)

    def solicitar_backup(self, nome_arquivo):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            
            mensagem = {
                'tipo': 'backup',
                'arquivo': nome_arquivo
            }
            self.enviar_mensagem(s, mensagem)

            resposta = self.receber_mensagem(s)
            if 'erro' in resposta:
                print(f"Erro: {resposta['erro']}")
                return
            
            servidor_principal = resposta['servidor_principal']
            servidor_replicado = resposta['servidor_replicado']

            self.enviar_arquivo(nome_arquivo, servidor_principal)
            self.enviar_arquivo(nome_arquivo, servidor_replicado)
        
        except Exception as e:
            print(f"Erro ao solicitar backup: {e}")

    def enviar_arquivo(self, nome_arquivo, servidor):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(servidor)

            with open(nome_arquivo, 'rb') as f:
                conteudo = f.read()

            mensagem = {
                'tipo': 'backup',
                'arquivo': nome_arquivo
            }
            self.enviar_mensagem(s, mensagem)
            s.sendall(conteudo)
            print(f"Arquivo {nome_arquivo} enviado para {servidor}")

        except Exception as e:
            print(f"Erro ao enviar o arquivo para {servidor}: {e}")
        finally:
            s.close()

    def receber_mensagem(self, client_socket):
        dados = b''
        while True:
            parte = client_socket.recv(4096)
            if not parte:
                break
            dados += parte
        return json.loads(dados.decode('utf-8'))

    def enviar_mensagem(self, client_socket, mensagem):
        mensagem_json = json.dumps(mensagem)
        client_socket.sendall(mensagem_json.encode('utf-8'))

if __name__ == '__main__':
    cliente = Cliente()
    cliente.iniciar()
