from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        'status': 'success',
        'message': 'AICEXPERT Backend is running!',
        'version': '1.0'
    })

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        'success': True,
        'message': 'API is working correctly',
        'method': request.method
    })

@app.route('/api/chat-simple', methods=['POST'])
def chat_simple():
    try:
        data = request.get_json()
        message = data.get('message', 'Hello')
        
        # Simple response for now
        return jsonify({
            'success': True,
            'content': f'Echo: {message}',
            'model': 'simple-echo'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

# Vercel handler
def handler(request, response):
    return app