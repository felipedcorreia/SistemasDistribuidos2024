import socket
import json
import os
import base64

class Message:
    def __init__(self, tipo, arquivo=None, conteudo=None):
        self.tipo = tipo
        self.arquivo = arquivo
        self.conteudo = conteudo

class Cliente:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port

    def iniciar(self):
        caminho_arquivo = input("Digite o caminho completo do arquivo para backup: ")
        if os.path.isfile(caminho_arquivo):
            self.solicitar_backup(caminho_arquivo)
        else:
            print("Arquivo não encontrado. Verifique o caminho e tente novamente.")

    def solicitar_backup(self, caminho_arquivo):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            print("Socket criado")

            mensagem = Message('backup', os.path.basename(caminho_arquivo))
            self.enviar_mensagem(s, mensagem)
            print("Mensagem de backup enviada ao gerenciador")

            resposta = self.receber_mensagem(s)
            print(f"Resposta recebida do gerenciador: {resposta}")
            if 'erro' in resposta:
                print(f"Erro: {resposta['erro']}")
                return
            
            servidor_principal = tuple(resposta['servidor_principal'])
            servidor_replicado = tuple(resposta['servidor_replicado'])

            self.enviar_arquivo(caminho_arquivo, servidor_principal)
            self.enviar_arquivo(caminho_arquivo, servidor_replicado)
        
        except Exception as e:
            print(f"Erro ao solicitar backup: {e}")

    def enviar_arquivo(self, caminho_arquivo, servidor):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(servidor)

            with open(caminho_arquivo, 'rb') as f:
                conteudo = f.read()

            tamanho_conteudo = len(conteudo)
            s.sendall(tamanho_conteudo.to_bytes(8, 'big'))

            # Codifica o conteúdo do arquivo em Base64
            conteudo_base64 = base64.b64encode(conteudo).decode('utf-8')

            # Cria a mensagem com o conteúdo codificado
            mensagem = {
                'tipo': 'backup',
                'arquivo': os.path.basename(caminho_arquivo),
                'conteudo': conteudo_base64
            }

            # Envia a mensagem para o servidor
            self.enviar_mensagem(s, mensagem)
            print(f"Arquivo {caminho_arquivo} enviado para {servidor}")

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
        try:
            if isinstance(mensagem, dict):
                mensagem_json = json.dumps(mensagem)
            else:
                # No caso de mensagem ser um objeto diferente de dict, se for necessário.
                mensagem_json = json.dumps(mensagem.__dict__)
                
            client_socket.sendall(mensagem_json.encode('utf-8'))
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

if __name__ == '__main__':
    cliente = Cliente()
    cliente.iniciar()
