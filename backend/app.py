from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from cerebras.cloud.sdk import Cerebras
import requests
import json

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Initialize Cerebras client
cerebras_api_key = os.getenv('CEREBRAS_API_KEY')
freepik_api_key = os.getenv('FREEPIK_API_KEY')

if cerebras_api_key:
    client = Cerebras(api_key=cerebras_api_key)
else:
    client = None
    print("Warning: CEREBRAS_API_KEY not found in environment variables")

# Health check endpoint
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'AICEXPERT Backend API is running',
        'version': '1.0.0',
        'apis': {
            'cerebras': 'configured' if cerebras_api_key else 'missing',
            'freepik': 'configured' if freepik_api_key else 'missing'
        }
    })

# API test endpoint  
@app.route('/api/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        'success': True,
        'message': 'API endpoint is working',
        'method': request.method,
        'cors': 'enabled'
    })

# Cerebras AI Chat endpoint
@app.route('/api/chat-simple', methods=['POST'])
def chat_simple():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Message field is required'}), 400

        # Check if Cerebras client is available
        if not client:
            return jsonify({
                'success': False,
                'error': 'Cerebras API not configured'
            }), 500

        # Call Cerebras API
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system", 
                        "content": "You are AICEXPERT, a helpful AI assistant. Provide concise, accurate, and helpful responses."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                model="llama3.1-8b",
                max_tokens=1000,
                temperature=0.7
            )
            
            # Extract response
            ai_response = chat_completion.choices[0].message.content
            
            return jsonify({
                'success': True,
                'content': ai_response,
                'model': 'llama3.1-8b'
            })
            
        except Exception as cerebras_error:
            print(f"Cerebras API error: {cerebras_error}")
            return jsonify({
                'success': False,
                'error': f'AI service error: {str(cerebras_error)}'
            }), 500
            
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Image generation endpoint
@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({'error': 'Prompt field is required'}), 400

        # Check if Freepik API key is available
        if not freepik_api_key:
            return jsonify({
                'success': False,
                'error': 'Freepik API not configured'
            }), 500

        # Call Freepik API for image generation
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-freepik-api-key': freepik_api_key
            }
            
            payload = {
                "prompt": prompt,
                "num_images": 1
            }
            
            response = requests.post(
                'https://api.freepik.com/v1/ai/text-to-image',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return jsonify({
                    'success': True,
                    'images': result.get('data', []),
                    'prompt': prompt
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Image generation failed: {response.text}'
                }), response.status_code
                
        except Exception as freepik_error:
            print(f"Freepik API error: {freepik_error}")
            return jsonify({
                'success': False,
                'error': f'Image generation service error: {str(freepik_error)}'
            }), 500
            
    except Exception as e:
        print(f"General error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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