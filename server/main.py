from flask import Flask
app = Flask(__name__)

@app.route("/")
def first_function():
        return "<html><body><h1 style='color:red'>I am hosted on Raspberry Pi !!!</h1></body></html>"

    if __name__ == "__main__":
            app.run(host='0.0.0.0')

