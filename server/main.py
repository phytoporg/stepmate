from flask import Flask
app = Flask(__name__)

@app.route("/")
def first_function():
    return "<html><body><h1 style='color:red'>I am hosted on Raspberry Pi !!!</h1></body></html>"

@app.route("/api/songs/list", methods=['GET'])
def list():
    return { 'songs' : [] }

if __name__ == "__main__":
    app.run(host='0.0.0.0')

