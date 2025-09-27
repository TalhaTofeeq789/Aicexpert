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
            
            # Updated payload based on Freepik API v1 documentation
            payload = {
                "prompt": prompt,
                "num_images": 1,
                "size": "1024x1024"
            }
            
            print(f"Calling Freepik API with prompt: {prompt}")  # Debug log
            response = requests.post(
                'https://api.freepik.com/v1/ai/text-to-image',
                headers=headers,
                json=payload,
                timeout=60  # Increased timeout for image generation
            )
            
            print(f"Freepik API response status: {response.status_code}")  # Debug log
            print(f"Freepik API response headers: {dict(response.headers)}")  # Debug log
            
            if response.status_code == 200:
                result = response.json()
                print(f"Freepik API result: {result}")  # Debug log
                
                # Extract images from the Freepik API response
                images = []
                
                # Check for 'data' array in response (most common format)
                if 'data' in result and isinstance(result['data'], list) and len(result['data']) > 0:
                    print(f"Found data array with {len(result['data'])} items")
                    
                    for i, item in enumerate(result['data']):
                        print(f"Processing item {i}: {type(item)}")
                        
                        if isinstance(item, dict):
                            print(f"Item keys: {list(item.keys())}")
                            
                            # First check for base64 data (which seems to be what we're getting)
                            if 'base64' in item and item['base64']:
                                base64_data = item['base64']
                                print(f"Found base64 image data, length: {len(base64_data)}")
                                
                                # Remove any data URL prefix if it exists and clean the base64 string
                                if base64_data.startswith('data:'):
                                    base64_data = base64_data.split(',', 1)[1]
                                
                                # Create data URL for base64 image
                                data_url = f"data:image/jpeg;base64,{base64_data}"
                                images.append(data_url)
                                print(f"Added base64 image as data URL")
                            
                            # Look for URL in different possible fields
                            elif 'url' in item and item['url']:
                                print(f"Found URL: {item['url']}")
                                images.append(item['url'])
                            elif 'image_url' in item and item['image_url']:
                                print(f"Found image_url: {item['image_url']}")
                                images.append(item['image_url'])
                            elif 'download_url' in item and item['download_url']:
                                print(f"Found download_url: {item['download_url']}")
                                images.append(item['download_url'])
                            else:
                                print(f"No recognizable image field found in item: {item}")
                                
                        elif isinstance(item, str) and item:
                            print(f"Found string item: {item}")
                            images.append(item)
                        else:
                            print(f"Unhandled item type or empty: {item}")
                
                # Fallback: check if response is direct URL list
                elif isinstance(result, list):
                    print("Response is a direct list")
                    images = [item for item in result if item]  # Filter out empty items
                
                # Fallback: check for single URL or base64
                elif isinstance(result, dict):
                    print("Response is a single dict, checking for direct fields")
                    if 'base64' in result and result['base64']:
                        base64_data = result['base64']
                        if base64_data.startswith('data:'):
                            base64_data = base64_data.split(',', 1)[1]
                        data_url = f"data:image/jpeg;base64,{base64_data}"
                        images = [data_url]
                    elif 'url' in result and result['url']:
                        images = [result['url']]
                
                print(f"Final extracted images count: {len(images)}")
                print(f"Images preview: {[img[:100] + '...' if len(img) > 100 else img for img in images]}")
                
                if images and len(images) > 0:
                    return jsonify({
                        'success': True,
                        'images': images,
                        'prompt': prompt
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'No images found in API response',
                        'raw_response': result,
                        'debug_info': {
                            'has_data': 'data' in result,
                            'data_type': type(result.get('data')) if 'data' in result else 'N/A',
                            'data_length': len(result.get('data', [])) if 'data' in result and isinstance(result.get('data'), list) else 'N/A',
                            'result_keys': list(result.keys()) if isinstance(result, dict) else 'N/A'
                        }
                    }), 500
                    
            else:
                error_text = response.text
                print(f"Freepik API error: {error_text}")
                
                # Handle specific error cases
                if response.status_code == 401:
                    error_msg = 'Invalid API key'
                elif response.status_code == 402:
                    error_msg = 'API quota exceeded'
                elif response.status_code == 429:
                    error_msg = 'Rate limit exceeded'
                else:
                    error_msg = f'API error (Status: {response.status_code}): {error_text}'
                
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