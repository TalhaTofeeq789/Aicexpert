import React, { useEffect, useState } from "react";

//import images
import avatar03 from "assets/images/avatar/03.png";
import avatar04 from "assets/images/avatar/04.png";
import { Link } from "react-router-dom";
import RightSidebar from "./RightSidebar";
import useSidebarToggle from "Common/UseSideberToggleHooks";

interface Message {
    role: 'user' | 'assistant' | 'system';
    content: string;
}

interface ChatResponse {
    success: boolean;
    content: string;
    model?: string;
    error?: string;
}

// Component to format AI responses
const FormattedMessage = ({ content }: { content: string }) => {
    const formatContent = (text: string) => {
        // Split by common markdown patterns
        const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|```[\s\S]*?```|#{1,6}\s[^\n]+|^\d+\.\s|\-\s)/gm);
        
        return parts.map((part, index) => {
            // Bold text (**text**)
            if (part.match(/^\*\*.*\*\*$/)) {
                return <strong key={index}>{part.replace(/\*\*/g, '')}</strong>;
            }
            
            // Inline code (`code`)
            if (part.match(/^`.*`$/)) {
                return <code key={index} style={{
                    backgroundColor: '#f4f4f4',
                    padding: '2px 4px',
                    borderRadius: '3px',
                    fontFamily: 'monospace',
                    fontSize: '0.9em'
                }}>{part.replace(/`/g, '')}</code>;
            }
            
            // Code blocks (```code```)
            if (part.match(/^```[\s\S]*```$/)) {
                const codeContent = part.replace(/```(\w+)?\n?/, '').replace(/```$/, '');
                return (
                    <pre key={index} style={{
                        backgroundColor: '#f8f8f8',
                        border: '1px solid #ddd',
                        borderRadius: '5px',
                        padding: '15px',
                        margin: '10px 0',
                        overflow: 'auto',
                        fontFamily: 'Monaco, Consolas, monospace',
                        fontSize: '0.9em',
                        lineHeight: '1.4'
                    }}>
                        <code>{codeContent}</code>
                    </pre>
                );
            }
            
            // Headers (# ## ###)
            if (part.match(/^#{1,6}\s/)) {
                const level = part.match(/^#+/)?.[0].length || 1;
                const text = part.replace(/^#+\s/, '');
                const Tag = `h${Math.min(level + 2, 6)}` as keyof JSX.IntrinsicElements;
                return <Tag key={index} style={{ margin: '15px 0 10px 0', color: '#333' }}>{text}</Tag>;
            }
            
            // Numbered lists
            if (part.match(/^\d+\.\s/)) {
                return <li key={index} style={{ margin: '5px 0' }}>{part.replace(/^\d+\.\s/, '')}</li>;
            }
            
            // Bullet points
            if (part.match(/^-\s/)) {
                return <li key={index} style={{ margin: '5px 0' }}>{part.replace(/^-\s/, '')}</li>;
            }
            
            // Regular text with line breaks
            if (part.includes('\n')) {
                return part.split('\n').map((line, lineIndex) => (
                    <span key={`${index}-${lineIndex}`}>
                        {line}
                        {lineIndex < part.split('\n').length - 1 && <br />}
                    </span>
                ));
            }
            
            return <span key={index}>{part}</span>;
        });
    };

    return (
        <div style={{ 
            lineHeight: '1.6', 
            color: '#333',
            wordWrap: 'break-word'
        }}>
            {formatContent(content)}
        </div>
    );
};

const Chatbot = () => {
    const themeSidebarToggle = useSidebarToggle();
    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'system',
            content: 'You are a helpful AI assistant.'
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isLoading) return;

        const userMessage: Message = {
            role: 'user',
            content: inputMessage.trim()
        };

        // Add user message to chat
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setInputMessage('');
        setIsLoading(true);

        try {
            // TODO: Replace 'your-actual-backend-url' with actual backend URL
            const apiUrl = process.env.REACT_APP_API_URL || 'https://your-actual-backend-url.vercel.app';
            console.log('API URL:', apiUrl); // Debug log
            const response = await fetch(`${apiUrl}/api/chat-simple`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: newMessages
                })
            });

            const data: ChatResponse = await response.json();

            if (data.success && data.content) {
                const assistantMessage: Message = {
                    role: 'assistant',
                    content: data.content
                };
                setMessages([...newMessages, assistantMessage]);
            } else {
                console.error('Error:', data.error);
                // Add error message to chat
                const errorMessage: Message = {
                    role: 'assistant',
                    content: 'Sorry, I encountered an error. Please try again.'
                };
                setMessages([...newMessages, errorMessage]);
            }
        } catch (error) {
            console.error('Network error:', error);
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Sorry, I could not connect to the server. Please check your connection and try again.'
            };
            setMessages([...newMessages, errorMessage]);
        } finally {
            setIsLoading(false);
        }
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
                    {messages.filter(m => m.role !== 'system').map((message, index) => (
                        <div key={index} className="single__question__answer">
                            {message.role === 'user' ? (
                                <div className="question_user">
                                    <div className="left_user_info">
                                        <img src={avatar03} alt="avatar" />
                                        <div className="question__user">{message.content}</div>
                                    </div>
                                    <div className="edit__icon openuptip">
                                        <i className="fa-regular fa-pen-to-square"></i>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="answer__area">
                                        <div className="thumbnail">
                                            <img src={avatar04} alt="avatar" />
                                        </div>
                                        <div className="answer_main__wrapper">
                                            <h4 className="common__title">AI Assistant</h4>
                                            <div className="disc">
                                                <FormattedMessage content={message.content} />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="share-reaction-area">
                                        <ul>
                                            <li><Link to="#" className="openuptip"><i className="fa-regular fa-bookmark"></i></Link></li>
                                            <li><Link to="#" className="openuptip"><i className="fa-light fa-thumbs-up"></i></Link></li>
                                            <li><Link to="#" className="openuptip"><i className="fa-regular fa-thumbs-down"></i></Link></li>
                                        </ul>
                                    </div>
                                </>
                            )}
                        </div>
                    ))}
                    
                    {isLoading && (
                        <div className="single__question__answer">
                            <div className="answer__area">
                                <div className="thumbnail">
                                    <img src={avatar04} alt="avatar" />
                                </div>
                                <div className="answer_main__wrapper">
                                    <h4 className="common__title">AI Assistant</h4>
                                    <p className="disc">
                                        Thinking...
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
                
                <form onSubmit={sendMessage} className="search-form">
                    <input 
                        type="text" 
                        placeholder="Message AI Assistant..." 
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        disabled={isLoading}
                    />
                    <button type="submit" disabled={isLoading || !inputMessage.trim()}>
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

export default Chatbot;