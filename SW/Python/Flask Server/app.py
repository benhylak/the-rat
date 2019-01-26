from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "index"

@app.route("/hello")
def hello():
    return "hello"

@app.route("/members")
def members():
    return "members"

@app.route("/members/<string:name>/")
def getMember(name):
    return name</string:name>

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
