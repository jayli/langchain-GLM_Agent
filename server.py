#coding = utf-8
from flask import Flask, jsonify, request, make_response
import json
from cli import answer

app = Flask(__name__)

@app.route('/ai/langchain/', methods=["POST"])
def handle_langchain_ask():
    if not request.form or not 'ask' in request.form:
        return make_response(jsonify({ "status": 500,
                                       "error":"error form params"}), 500)
    ask = request.form.get('ask')
    content = answer(ask)
    return make_response(jsonify({ 'status': 200,
                                   'content': content}), 200)

if __name__ == "__main__":
    app.run(debug=False, port=8899, host="127.0.0.1")
