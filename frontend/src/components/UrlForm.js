import React, { useState } from 'react';

const UrlForm = ({ models, audiences, onGenerate, loading }) => {
    const [url, setUrl] = useState('');
    const [model, setModel] = useState('gpt2');
    const [audience, setAudience] = useState('business');
    const [apiToken, setApiToken] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!url.trim()) {
            alert('Please enter a URL');
            return;
        }

        onGenerate({
            type: 'url',
            url: url.trim(),
            model,
            audience,
            api_token: apiToken || undefined
        });
    };

    return (
        <div>
            <h2>Generate Newsletter from URL</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="url">Article URL:</label>
                    <input
                        type="url"
                        id="url"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="https://example.com/article"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="model">AI Model:</label>
                    <select
                        id="model"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                    >
                        {models.map((modelOption) => (
                            <option key={modelOption.id} value={modelOption.id}>
                                {modelOption.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="audience">Target Audience:</label>
                    <select
                        id="audience"
                        value={audience}
                        onChange={(e) => setAudience(e.target.value)}
                    >
                        {audiences.map((audienceOption) => (
                            <option key={audienceOption.id} value={audienceOption.id}>
                                {audienceOption.name}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label htmlFor="apiToken">API Token (optional):</label>
                    <input
                        type="password"
                        id="apiToken"
                        value={apiToken}
                        onChange={(e) => setApiToken(e.target.value)}
                        placeholder="Enter API token if required"
                    />
                </div>

                <button
                    type="submit"
                    className="btn"
                    disabled={loading || !url.trim()}
                >
                    {loading ? 'Generating...' : 'Generate Newsletter'}
                </button>
            </form>
        </div>
    );
};

export default UrlForm; 