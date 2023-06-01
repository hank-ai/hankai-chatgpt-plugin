from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    # 0.0.0.0 makes the server accessible from any IP
    app.run(host='0.0.0.0', port=5003)
