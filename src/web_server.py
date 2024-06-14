import socket
import os
import json
import platform
import sys
import mimetypes

# Configuración del servidor
TCP_IP = "0.0.0.0"
TCP_PORT = 12345

PREFIX = "src/web/"

# Crear un socket TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(5)  # Permitir múltiples conexiones entrantes

print(f"Servidor TCP escuchando en el puerto {TCP_PORT}")

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "text/plain"

def get_computer_info():
    return {
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": platform.system(),
        "python_version": sys.version.split()[0]
    }

while True:
    try:
        # Esperar por una conexión entrante
        conn, addr = sock.accept()
        print(f"Conexión establecida con: {addr}")

        # Esperar a recibir una solicitud HTTP
        print("Antes de RECV")
        data = conn.recv(1024).decode('utf-8')  # buffer size is 1024 bytes
        print("Despues de RECV")
        if data:
            print(f"Solicitud recibida de {addr}")
            request_line = data.splitlines()[0]
            request_method, path, _ = request_line.split()
            print(f"Solicitud: {request_method} {path}")

            if request_method == "GET":
                if path == "/":
                    file_path = PREFIX + "index.html"
                elif path == "/info":
                    file_path = PREFIX + "info.html"
                elif path == "/info.json":
                    file_path = None
                    response_body = json.dumps(get_computer_info())
                elif path == "/screen":
                    file_path = PREFIX + "screen.html"
                else:
                    file_path = PREFIX + path.lstrip("/")

                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as file:
                        response_body = file.read()

                    response_headers = "HTTP/1.1 200 OK\r\n"
                    response_headers += f"Content-Type: {get_mime_type(file_path)}\r\n"
                    response_headers += f"Content-Length: {len(response_body)}\r\n"
                    response_headers += "\r\n"

                    response = response_headers.encode('utf-8') + response_body
                elif file_path is None:
                    response_headers = "HTTP/1.1 200 OK\r\n"
                    response_headers += "Content-Type: application/json; charset=UTF-8\r\n"
                    response_headers += f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
                    response_headers += "\r\n"

                    response = response_headers.encode('utf-8') + response_body.encode('utf-8')
                else:
                    response_body = "<h1>404 Not Found</h1>"
                    response_headers = "HTTP/1.1 404 Not Found\r\n"
                    response_headers += "Content-Type: text/html; charset=UTF-8\r\n"
                    response_headers += f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
                    response_headers += "\r\n"

                    response = response_headers.encode('utf-8') + response_body.encode('utf-8')

                conn.sendall(response)

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.close()
