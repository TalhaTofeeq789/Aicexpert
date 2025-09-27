# Image Generator Backend

This is a simple Flask backend that acts as a proxy for the Freepik API to avoid CORS issues.

## Setup Instructions

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend Server
```bash
python app.py
```

Or on Windows, double-click: `start_backend.bat`

### 3. Backend Endpoints

- **POST** `/api/generate-image` - Generate images
  - Body: `{"prompt": "your image description"}`
  - Returns: `{"success": true, "images": ["url1", "url2"], "prompt": "..."}`

- **GET** `/health` - Health check
  - Returns: `{"status": "Backend is running!"}`

### 4. Start the Frontend
```bash
cd ..
npm start
```

The frontend will now use the backend (http://localhost:5000) instead of calling Freepik API directly.

## How it Works

1. React frontend sends requests to Flask backend (localhost:5000)
2. Flask backend forwards requests to Freepik API
3. Backend polls for completion and returns results to frontend
4. Frontend displays the generated images

This setup resolves CORS issues since the API calls are made server-side.