import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import UrlForm from './components/UrlForm';
import FileUpload from './components/FileUpload';
import NewsletterDisplay from './components/NewsletterDisplay';

function App() {
    const [activeTab, setActiveTab] = useState('url');
    const [newsletter, setNewsletter] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [models, setModels] = useState([]);
    const [audiences, setAudiences] = useState([]);

    useEffect(() => {
        // Fetch available models and audiences
        const fetchOptions = async () => {
            try {
                const [modelsResponse, audiencesResponse] = await Promise.all([
                    axios.get('/api/models'),
                    axios.get('/api/audiences')
                ]);
                setModels(modelsResponse.data);
                setAudiences(audiencesResponse.data);
            } catch (err) {
                console.error('Error fetching options:', err);
            }
        };

        fetchOptions();
    }, []);

    const handleGenerateNewsletter = async (data) => {
        setLoading(true);
        setError(null);
        setNewsletter(null);

        try {
            let response;

            if (data.type === 'url') {
                response = await axios.post('/api/generate-from-url', {
                    url: data.url,
                    model: data.model,
                    audience: data.audience,
                    api_token: data.api_token
                });
            } else if (data.type === 'file') {
                const formData = new FormData();
                formData.append('file', data.file);
                formData.append('model', data.model);
                formData.append('audience', data.audience);
                if (data.api_token) {
                    formData.append('api_token', data.api_token);
                }

                response = await axios.post('/api/generate-from-file', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            }

            setNewsletter(response.data);
        } catch (err) {
            setError(err.response?.data?.error || 'An error occurred while generating the newsletter');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="App">
            <div className="container">
                <div className="header">
                    <h1>📰 Newsletter Generator</h1>
                    <p>Create professional newsletters from URLs or documents using AI</p>
                </div>

                <div className="card">
                    <div className="tabs">
                        <button
                            className={`tab ${activeTab === 'url' ? 'active' : ''}`}
                            onClick={() => setActiveTab('url')}
                        >
                            📄 Generate from URL
                        </button>
                        <button
                            className={`tab ${activeTab === 'file' ? 'active' : ''}`}
                            onClick={() => setActiveTab('file')}
                        >
                            📁 Upload File (PDF/DOCX)
                        </button>
                    </div>

                    <div className={`tab-content ${activeTab === 'url' ? 'active' : ''}`}>
                        <UrlForm
                            models={models}
                            audiences={audiences}
                            onGenerate={handleGenerateNewsletter}
                            loading={loading}
                        />
                    </div>

                    <div className={`tab-content ${activeTab === 'file' ? 'active' : ''}`}>
                        <FileUpload
                            models={models}
                            audiences={audiences}
                            onGenerate={handleGenerateNewsletter}
                            loading={loading}
                        />
                    </div>
                </div>

                {error && (
                    <div className="card">
                        <div className="error">
                            <strong>Error:</strong> {error}
                        </div>
                    </div>
                )}

                {loading && (
                    <div className="card">
                        <div className="loading">
                            <div className="loading-spinner"></div>
                            <p>Generating your newsletter... This may take a few moments.</p>
                        </div>
                    </div>
                )}

                {newsletter && (
                    <div className="card">
                        <NewsletterDisplay newsletter={newsletter} />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App; 