from flask import Flask, send_file
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, Flask is working!"

if __name__ == '__main__':
    app.run(debug=True)
