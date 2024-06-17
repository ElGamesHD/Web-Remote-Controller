from flask import Flask, render_template
import socket
import platform
import sys

app = Flask(__name__)
screen_server_port = 36743

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/info')
def info():
    return render_template('info.html', info={
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": platform.system(),
        "python_version": sys.version.split()[0]
    })

@app.route('/screen')
def screen():
    return render_template('screen.html', ip=socket.gethostbyname(socket.gethostname()), port=screen_server_port)

def main():
    app.run(host='0.0.0.0', port=12345)

if __name__ == "__main__":
    main()