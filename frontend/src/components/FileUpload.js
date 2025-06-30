import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ models, audiences, onGenerate, loading }) => {
    const [model, setModel] = useState('gpt2');
    const [audience, setAudience] = useState('business');
    const [apiToken, setApiToken] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);

    const onDrop = useCallback((acceptedFiles) => {
        if (acceptedFiles.length > 0) {
            setSelectedFile(acceptedFiles[0]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        },
        multiple: false
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!selectedFile) {
            alert('Please select a file');
            return;
        }

        onGenerate({
            type: 'file',
            file: selectedFile,
            model,
            audience,
            api_token: apiToken || undefined
        });
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedFile(file);
        }
    };

    return (
        <div>
            <h2>Generate Newsletter from File</h2>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Upload File (PDF or DOCX):</label>
                    <div
                        {...getRootProps()}
                        className={`dropzone ${isDragActive ? 'dragover' : ''}`}
                    >
                        <input {...getInputProps()} />
                        {selectedFile ? (
                            <div>
                                <p>✅ Selected: {selectedFile.name}</p>
                                <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                        ) : (
                            <div>
                                <p>📁 Drag & drop a PDF or DOCX file here, or click to select</p>
                                <p>Maximum file size: 16MB</p>
                            </div>
                        )}
                    </div>

                    {/* Fallback file input for browsers that don't support drag & drop */}
                    <input
                        type="file"
                        accept=".pdf,.docx"
                        onChange={handleFileSelect}
                        style={{ marginTop: '10px' }}
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
                    disabled={loading || !selectedFile}
                >
                    {loading ? 'Generating...' : 'Generate Newsletter'}
                </button>
            </form>
        </div>
    );
};

export default FileUpload; 