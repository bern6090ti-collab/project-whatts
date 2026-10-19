from flask import Flask
import socket
import threading
import json
import random
import os

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 5500))
clients = {}
users = {}

def gerar_numero_unico():
    while True:
        num = random.randint(100000, 999999)
        if str(num) not in users:
            return str(num)

@app.route('/')
def home():
    return "🚀 MAX CHAT Servidor Online!"

def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(10)
    print(f"🚀 Servidor rodando na porta {PORT}")
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def handle_client(conn, addr):
    user_id = None
    try:
        while True:
            data = conn.recv(8192).decode()
            if not data: break
            msg = json.loads(data)
            
            if msg["type"] == "register":
                user_id = gerar_numero_unico()
                users[user_id] = {"name": msg["name"], "status": "online"}
                clients[user_id] = conn
                conn.send(json.dumps({"type": "registered", "id": user_id}).encode())
                print(f"✅ Novo usuário: {user_id}")
            
            elif msg["type"] == "login":
                user_id = msg["user_id"]
                if user_id in users:
                    clients[user_id] = conn
                    conn.send(json.dumps({"type": "login_ok", "profile": users[user_id]}).encode())
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if user_id and user_id in clients:
            del clients[user_id]
        conn.close()

if __name__ == "__main__":
    threading.Thread(target=start_socket_server, daemon=True).start()
    app.run(host="0.0.0.0", port=PORT)