from flask import Flask, jsonify, render_template, send_from_directory
import socket
import platform
import sys

app = Flask(__name__)

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
    return render_template('screen.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12345)
