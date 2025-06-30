import React from 'react';

const NewsletterDisplay = ({ newsletter }) => {
    const handleDownload = () => {
        const dataStr = JSON.stringify(newsletter, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

        const exportFileDefaultName = 'newsletter.json';

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportFileDefaultName);
        linkElement.click();
    };

    const handleCopyToClipboard = () => {
        const newsletterText = `
${newsletter.headline}

${newsletter.introduction}

${newsletter.sections.map((section, index) => `Section ${index + 1}: ${section}`).join('\n\n')}

Call to Action: ${newsletter.cta}
    `.trim();

        navigator.clipboard.writeText(newsletterText).then(() => {
            alert('Newsletter copied to clipboard!');
        }).catch(() => {
            alert('Failed to copy to clipboard');
        });
    };

    return (
        <div className="newsletter-output">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3>Generated Newsletter</h3>
                <div>
                    <button onClick={handleCopyToClipboard} className="btn btn-secondary">
                        📋 Copy Text
                    </button>
                    <button onClick={handleDownload} className="btn btn-secondary">
                        💾 Download JSON
                    </button>
                </div>
            </div>

            <div className="headline">
                {newsletter.headline}
            </div>

            <div className="introduction">
                {newsletter.introduction}
            </div>

            {newsletter.sections && newsletter.sections.map((section, index) => (
                <div key={index} className="section">
                    <h4>Section {index + 1}</h4>
                    <p>{section}</p>
                </div>
            ))}

            {newsletter.cta && (
                <div className="cta">
                    {newsletter.cta}
                </div>
            )}

            {newsletter.raw_output && (
                <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                    <h4>Raw Output:</h4>
                    <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                        {newsletter.raw_output}
                    </pre>
                </div>
            )}
        </div>
    );
};

export default NewsletterDisplay; 