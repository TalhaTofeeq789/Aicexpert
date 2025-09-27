from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Get API keys from environment
cerebras_api_key = os.getenv('CEREBRAS_API_KEY')
freepik_api_key = os.getenv('FREEPIK_API_KEY')

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

# Test image generation endpoint with mock data
@app.route('/api/test-image', methods=['POST'])
def test_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', 'test image')
        
        # Return mock successful response
        return jsonify({
            'success': True,
            'images': [
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1024&q=80'
            ],
            'prompt': prompt,
            'mock': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Cerebras AI Chat endpoint using direct HTTP calls
@app.route('/api/chat-simple', methods=['POST'])
def chat_simple():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Message field is required'}), 400

        # Check if Cerebras API key is available
        if not cerebras_api_key:
            return jsonify({
                'success': False,
                'error': 'Cerebras API not configured'
            }), 500

        # Call Cerebras API directly with HTTP requests
        try:
            headers = {
                'Authorization': f'Bearer {cerebras_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "llama3.1-8b",
                "messages": [
                    {
                        "role": "system", 
                        "content": "You are AICEXPERT, a helpful AI assistant. Provide concise, accurate, and helpful responses."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                'https://api.cerebras.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                return jsonify({
                    'success': True,
                    'content': ai_response,
                    'model': 'llama3.1-8b'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'AI service error: {response.text}'
                }), response.status_code
            
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
            
            print(f"Calling Freepik API with prompt: {prompt}")  # Debug log
            response = requests.post(
                'https://api.freepik.com/v1/ai/text-to-image',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Freepik API response status: {response.status_code}")  # Debug log
            print(f"Freepik API response: {response.text}")  # Debug log
            
            if response.status_code == 200:
                result = response.json()
                print(f"Freepik API result: {result}")  # Debug log
                
                # Handle different possible response formats
                images = []
                if 'data' in result:
                    # Standard format: {data: [{url: "...", ...}]}
                    for img_data in result['data']:
                        if isinstance(img_data, dict) and 'url' in img_data:
                            images.append(img_data['url'])
                        elif isinstance(img_data, str):
                            images.append(img_data)
                elif 'images' in result:
                    # Alternative format: {images: ["url1", "url2"]}
                    images = result['images']
                elif 'url' in result:
                    # Single URL format: {url: "..."}
                    images = [result['url']]
                
                return jsonify({
                    'success': True,
                    'images': images,
                    'prompt': prompt,
                    'raw_response': result  # Include raw response for debugging
                })
            else:
                error_msg = f'Image generation failed (Status: {response.status_code}): {response.text}'
                print(f"Freepik API error: {error_msg}")
                return jsonify({
                    'success': False,
                    'error': error_msg
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

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Main entry point
if __name__ == '__main__':
    app.run(debug=False)

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