from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)

# Configure CORS with specific origins
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://aicexpert-frontend.vercel.app",
            "http://localhost:3000",
            "https://localhost:3000"
        ],
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
        "supports_credentials": True
    }
})

# Add CORS headers manually for all responses
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ["https://aicexpert-frontend.vercel.app", "http://localhost:3000", "https://localhost:3000"]:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Health check endpoint
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'AICEXPERT Backend API is running',
        'version': '1.0.0'
    })

# API test endpoint  
@app.route('/api/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        'success': True,
        'message': 'API endpoint is working',
        'method': request.method
    })

# Simple chat endpoint
@app.route('/api/chat-simple', methods=['POST', 'OPTIONS'])
def chat_simple():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Message field is required'}), 400
        
        # Simple echo response for testing
        response = f"Hello! You said: {message}. This is a test response from AICEXPERT backend."
        
        return jsonify({
            'success': True,
            'content': response,
            'model': 'test-echo'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Global OPTIONS handler for preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)