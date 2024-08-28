from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hellow,World"


if __name__ == "__main__":
    # 使用するポートを明示
    app.run(port=8000, debug=True)
