import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import RightSidebar from "./RightSidebar";

//import images
import avatar03 from "assets/images/avatar/03.png";
import avatar04 from "assets/images/avatar/04.png";
import icon15 from "assets/images/icons/15.png";
import useSidebarToggle from "Common/UseSideberToggleHooks";

// Backend API configuration - HARDCODED for stability
const BACKEND_URL = "https://aicexpert.vercel.app";
console.log('🎨 Image Generator API URL:', BACKEND_URL); // Debug log

interface GeneratedImage {
    url: string;
    prompt: string;
    timestamp: number;
}

interface GenerationState {
    loading: boolean;
    progress: number;
    error: string | null;
}

const ImageGenerator = () => {
    const themeSidebarToggle = useSidebarToggle();
    
    // State for image generation
    const [prompt, setPrompt] = useState<string>('');
    const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
    const [generationState, setGenerationState] = useState<GenerationState>({
        loading: false,
        progress: 0,
        error: null
    });

    // API function to generate images
    const generateImage = async (userPrompt: string) => {
        try {
            setGenerationState({ loading: true, progress: 10, error: null });
            
            const payload = {
                prompt: userPrompt
            };

            // Call the backend API
            setGenerationState(prev => ({ ...prev, progress: 20 }));
            console.log('🔗 Full image endpoint:', `${BACKEND_URL}/api/generate-image`); // Debug log
            console.log('📝 Payload:', payload); // Debug log
            
            const response = await fetch(`${BACKEND_URL}/api/generate-image`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            console.log('📡 Image Response status:', response.status); // Debug log
            console.log('📡 Image Response ok:', response.ok); // Debug log

            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ Image API Error:', errorText);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            console.log('📨 Image Response data:', data); // Debug log
            
            if (data.success && data.images && data.images.length > 0) {
                setGenerationState(prev => ({ ...prev, progress: 100 }));
                
                const newImages: GeneratedImage[] = data.images.map((imageUrl: string) => ({
                    url: imageUrl, // imageUrl is now directly the URL (either HTTP URL or data URL)
                    prompt: userPrompt,
                    timestamp: Date.now()
                }));

                console.log('✅ Generated images:', newImages); // Debug log
                setGeneratedImages(prev => [...newImages, ...prev]);
                setGenerationState({ loading: false, progress: 100, error: null });
            } else {
                console.error('❌ Image generation failed:', data);
                throw new Error(data.error || 'No images generated');
            }

        } catch (error) {
            console.error('Error generating image:', error);
            setGenerationState({
                loading: false,
                progress: 0,
                error: error instanceof Error ? error.message : 'Failed to generate image'
            });
        }
    };

    // Handle form submission
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim() || generationState.loading) return;
        
        await generateImage(prompt.trim());
        setPrompt(''); // Clear input after submission
    };

    useEffect(() => {
        document.body.classList.add("chatbot");

        return () => {
            document.body.classList.remove("chatbot");
        };
    }, []);

    useEffect(() => {
        const handleScroll = () => {
            const distanceFromBottom = document.documentElement.scrollHeight - window.innerHeight - window.scrollY;

            const threshold = 200;
            const searchForm: any = document.querySelector('.chatbot .search-form');

            if (distanceFromBottom < threshold) {
                searchForm.classList.add('active');
            } else {
                searchForm.classList.remove('active');
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    return (
        <>
            <div className={`main-center-content-m-left center-content search-sticky ${themeSidebarToggle ? "collapsed" : ""}`}>

                <div className="question_answer__wrapper__chatbot">
                    {/* Show error if any */}
                    {generationState.error && (
                        <div className="single__question__answer">
                            <div className="answer__area">
                                <div className="thumbnail">
                                    <img src={avatar04} alt="avatar" />
                                </div>
                                <div className="answer_main__wrapper">
                                    <h4 className="common__title" style={{color: 'red'}}>Error</h4>
                                    <p className="disc">{generationState.error}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Show loading progress */}
                    {generationState.loading && (
                        <div className="single__question__answer">
                            <div className="answer__area">
                                <div className="thumbnail">
                                    <img src={avatar04} alt="avatar" />
                                </div>
                                <div className="answer_main__wrapper">
                                    <h4 className="common__title">Generating Image...</h4>
                                    <p className="disc">Please wait while I create your image. This may take up to 2 minutes.</p>
                                    
                                    {/* Progress Bar */}
                                    <div style={{
                                        width: '100%',
                                        height: '20px',
                                        backgroundColor: '#f0f0f0',
                                        borderRadius: '10px',
                                        overflow: 'hidden',
                                        marginTop: '20px'
                                    }}>
                                        <div style={{
                                            width: `${generationState.progress}%`,
                                            height: '100%',
                                            backgroundColor: '#4CAF50',
                                            transition: 'width 0.3s ease',
                                            borderRadius: '10px'
                                        }}></div>
                                    </div>
                                    <p style={{marginTop: '10px', fontSize: '14px', color: '#666'}}>
                                        Progress: {Math.round(generationState.progress)}%
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Display generated images */}
                    {generatedImages.map((imageData, index) => (
                        <div key={`${imageData.timestamp}-${index}`} className="single__question__answer">
                            <div className="question_user">
                                <div className="left_user_info">
                                    <img src={avatar03} alt="avatar" />
                                    <div className="question__user">{imageData.prompt}</div>
                                </div>
                                <div className="edit__icon openuptip">
                                    <i className="fa-regular fa-pen-to-square"></i>
                                </div>
                            </div>
                            <div className="answer__area">
                                <div className="thumbnail">
                                    <img src={avatar04} alt="avatar" />
                                </div>
                                <div className="answer_main__wrapper">
                                    <h4 className="common__title">AI Generated Image</h4>
                                    <p className="disc">
                                        Here's your generated image based on the prompt: "{imageData.prompt}"
                                    </p>
                                    <div className="generated_image__wraper">
                                        <div className="top-images-area gallery-image-generator">
                                            <div className="gallery-display-item-wrapper">
                                                <div className="gallery__images-item one">
                                                    <Link to={`#generated-${index}`} className="gallery__images-link">
                                                        <img src={imageData.url} alt="Generated image" />
                                                    </Link>
                                                </div>
                                            </div>

                                            <div className="gallery__lightbox" id={`generated-${index}`}>
                                                <div className="gallery__lightbox-content">
                                                    <Link to="#0" className="close">
                                                        ×
                                                    </Link>
                                                    <img src={imageData.url} className="gallery__lightbox-image" alt="Generated image" />
                                                </div>
                                            </div>
                                        </div>
                                        <div className="bottom-image">
                                            <p>"{imageData.prompt}"</p>
                                            <div className="botton-content-between">
                                                <div className="left-area">
                                                    <img src={icon15} alt="icons" />
                                                    <span className="tags">Powered by Freepik AI</span>
                                                </div>
                                                <div className="share-reaction-area">
                                                    <ul>
                                                        <li><Link to="#" className="openuptip"><i className="fa-regular fa-bookmark"></i></Link></li>
                                                        <li><Link to="#" className="openuptip"><i className="fa-light fa-thumbs-up"></i></Link></li>
                                                        <li><Link to="#" className="openuptip"><i className="fa-regular fa-thumbs-down"></i></Link></li>
                                                        <li><Link to="#" className="openuptip"><i className="fa-light fa-download"></i></Link></li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <form onSubmit={handleSubmit} className="search-form">
                    <input 
                        type="text" 
                        placeholder="Describe the image you want to generate..." 
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        disabled={generationState.loading}
                    />
                    <button type="submit" disabled={generationState.loading || !prompt.trim()}>
                        <i className="fa-regular fa-arrow-up"></i>
                    </button>
                </form>

                <div className="copyright-area-bottom">
                    <p> <Link to="#">Reactheme©</Link> 2024. All Rights Reserved.</p>
                </div>
            </div>

            <RightSidebar />
        </>
    );
};

export default ImageGenerator;