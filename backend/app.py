from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import time
import json
import os
from cerebras.cloud.sdk import Cerebras

app = Flask(__name__)

# Get CORS origins from environment variable
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, origins=allowed_origins)

# Freepik API configuration
API_KEY = os.getenv('FREEPIK_API_KEY')
if not API_KEY:
    print("Warning: FREEPIK_API_KEY environment variable not set!")
BASE_URL = "https://api.freepik.com/v1/ai/mystic"

# Cerebras API configuration
CEREBRAS_API_KEY = os.getenv('CEREBRAS_API_KEY')
if not CEREBRAS_API_KEY:
    print("Warning: CEREBRAS_API_KEY environment variable not set!")

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400

        headers = {
            "Content-Type": "application/json",
            "x-freepik-api-key": API_KEY
        }

        payload = {
            "prompt": prompt,
            "resolution": "2k",
            "aspect_ratio": "square_1_1",
            "model": "realism"
        }

        # Step 1: Send generation request
        print(f"Sending generation request for prompt: {prompt}")
        response = requests.post(BASE_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Error in generation: {response.status_code} - {response.text}")
            return jsonify({'error': f'API Error: {response.status_code}'}), 500

        data = response.json()
        task_id = data["data"]["task_id"]
        print(f"Task ID: {task_id}")

        # Step 2: Poll for completion
        status_url = f"{BASE_URL}/{task_id}"
        max_attempts = 30  # ~2.5 minutes max
        
        for attempt in range(max_attempts):
            print(f"Checking status... Attempt {attempt + 1}/{max_attempts}")
            
            time.sleep(5)  # Wait 5 seconds between checks
            
            check_response = requests.get(status_url, headers=headers)
            check_data = check_response.json()
            status = check_data["data"]["status"]
            
            print(f"Status: {status}")
            
            if status == "COMPLETED":
                image_urls = check_data["data"]["generated"]
                print(f"Generation completed! Images: {image_urls}")
                return jsonify({
                    'success': True,
                    'images': image_urls,
                    'prompt': prompt
                })
            elif status == "FAILED":
                print("Generation failed")
                return jsonify({'error': 'Image generation failed'}), 500

        print("Generation timed out")
        return jsonify({'error': 'Generation timed out'}), 408

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<task_id>', methods=['GET'])
def check_status(task_id):
    try:
        headers = {
            "Content-Type": "application/json",
            "x-freepik-api-key": API_KEY
        }
        
        status_url = f"{BASE_URL}/{task_id}"
        response = requests.get(status_url, headers=headers)
        
        if response.status_code != 200:
            return jsonify({'error': f'API Error: {response.status_code}'}), 500
            
        data = response.json()
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'Backend is running!'})

@app.route('/api/chat', methods=['POST'])
def chat_with_cerebras():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'Messages are required'}), 400

        # Initialize Cerebras client
        client = Cerebras(api_key=CEREBRAS_API_KEY)

        # Create a streaming chat completion
        stream = client.chat.completions.create(
            messages=messages,
            model="qwen-3-235b-a22b-instruct-2507",
            stream=True,
            max_completion_tokens=2000,
            temperature=0.7,
            top_p=0.8
        )

        def generate():
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield f"data: {json.dumps({'content': content})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat-simple', methods=['POST'])
def chat_simple():
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'Messages are required'}), 400

        # Add system instructions for better formatting
        enhanced_messages = []
        system_found = False
        
        for msg in messages:
            if msg.get('role') == 'system':
                enhanced_msg = {
                    'role': 'system',
                    'content': msg.get('content', '') + '''

Please format your responses clearly and readably:
- Use **bold** for important terms
- Use `code` for inline code snippets  
- Use ```language blocks for multi-line code
- Use proper headings with # ## ###
- Use numbered lists (1. 2. 3.) for steps
- Use bullet points (-) for lists
- Add proper spacing between sections
- Keep explanations clear and concise
- Always include practical examples when explaining code concepts'''
                }
                enhanced_messages.append(enhanced_msg)
                system_found = True
            else:
                enhanced_messages.append(msg)
        
        # If no system message exists, add one
        if not system_found:
            enhanced_messages.insert(0, {
                'role': 'system',
                'content': '''You are a helpful programming assistant. Format your responses clearly:
- Use **bold** for important terms
- Use `code` for inline code snippets  
- Use ```language blocks for multi-line code
- Use proper headings with # ## ###
- Use numbered lists (1. 2. 3.) for steps
- Use bullet points (-) for lists
- Add proper spacing between sections
- Keep explanations clear and concise
- Always include practical examples when explaining code concepts'''
            })

        # Initialize Cerebras client
        client = Cerebras(api_key=CEREBRAS_API_KEY)

        # Create a non-streaming chat completion for simpler frontend integration
        response = client.chat.completions.create(
            messages=enhanced_messages,
            model="qwen-3-235b-a22b-instruct-2507",
            stream=False,
            max_completion_tokens=2000,
            temperature=0.7,
            top_p=0.8
        )

        return jsonify({
            'success': True,
            'content': response.choices[0].message.content,
            'model': response.model
        })

    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask backend server...")
    print("Backend will be available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)