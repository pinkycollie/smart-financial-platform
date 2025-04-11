from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'MbTQ Financial Platform API',
        'status': 'running',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)