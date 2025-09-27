// Temporary test file to check image generation frontend
// Backend API configuration - HARDCODED for stability
const BACKEND_URL = "https://aicexpert.vercel.app";

async function testImageGeneration() {
    try {
        console.log('Testing image generation...');
        
        const response = await fetch(`${BACKEND_URL}/api/test-image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: 'test beautiful landscape'
            })
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.success && data.images) {
            console.log('Images received:', data.images);
            data.images.forEach((url, index) => {
                console.log(`Image ${index + 1}:`, url);
            });
        }
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run test
testImageGeneration();