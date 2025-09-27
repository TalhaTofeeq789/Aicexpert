# Vercel Deployment Guide

## Prerequisites
1. GitHub account
2. Vercel account
3. Your code pushed to GitHub repository

## Deployment Steps

### 1. Backend Deployment (Flask API)
1. Create a separate GitHub repository for backend
2. Copy all files from `/backend` folder to the new repo
3. Push to GitHub
4. Go to Vercel Dashboard
5. Click "New Project"
6. Import your backend repository
7. Configure Environment Variables:
   - `CEREBRAS_API_KEY`: Your Cerebras API key
   - `FREEPIK_API_KEY`: Your Freepik API key
   - `ALLOWED_ORIGINS`: Your frontend URL (will get after frontend deployment)
8. Deploy

### 2. Frontend Deployment (React App)
1. Create another GitHub repository for frontend
2. Copy all files from main project folder (excluding `/backend`) to new repo
3. Update `.env` file with your backend URL
4. Push to GitHub
5. Go to Vercel Dashboard
6. Click "New Project"
7. Import your frontend repository
8. Configure Environment Variables:
   - `REACT_APP_API_URL`: Your backend URL from step 1
   - `GENERATE_SOURCEMAP`: false
9. Deploy

### 3. Update CORS Settings
1. After frontend deployment, copy the frontend URL
2. Go to backend project in Vercel
3. Update environment variable `ALLOWED_ORIGINS` with frontend URL
4. Redeploy backend

## Important Notes
- Keep API keys secure in environment variables
- Never commit API keys to GitHub
- Update CORS origins after deployment
- Test all endpoints after deployment

## Files Created for Deployment
- `/vercel.json` - Frontend configuration
- `/backend/vercel.json` - Backend configuration
- `/.env` - Frontend environment variables
- `/backend/.env` - Backend environment variables
- Updated Chatbot API URL to use environment variable
- Updated backend CORS configuration