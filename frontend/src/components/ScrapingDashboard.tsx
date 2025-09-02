import React, { useState } from 'react';
import { triggerEmailScraping, triggerWhatsappAnalysis, triggerInstagramScraping } from '../services/api';

// A reusable component for displaying API call results
const ResultDisplay = ({ title, data }: { title: string, data: any }) => {
    if (!data) return null;
    return (
        <div className="mt-3">
            <h5>{title}</h5>
            <pre className="bg-light p-2 rounded"><code>{JSON.stringify(data, null, 2)}</code></pre>
        </div>
    );
};

const ScrapingDashboard: React.FC = () => {
    const [isLoading, setIsLoading] = useState<Record<string, boolean>>({});
    const [error, setError] = useState<Record<string, string | null>>({});
    const [data, setData] = useState<Record<string, any>>({});
    const [instaUsername, setInstaUsername] = useState('snuc_omnia');

    const handleApiCall = async (apiKey: string, apiFn: () => Promise<any>) => {
        setIsLoading(prev => ({ ...prev, [apiKey]: true }));
        setError(prev => ({ ...prev, [apiKey]: null }));
        try {
            const result = await apiFn();
            setData(prev => ({ ...prev, [apiKey]: result }));
        } catch (err: any) {
            setError(prev => ({ ...prev, [apiKey]: err.message }));
        } finally {
            setIsLoading(prev => ({ ...prev, [apiKey]: false }));
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3>Data Scraping Tools</h3>
            </div>
            <div className="card-body">
                {/* WhatsApp */}
                <div className="mb-3">
                    <button className="btn btn-primary w-100" onClick={() => handleApiCall('whatsapp', triggerWhatsappAnalysis)} disabled={isLoading['whatsapp']}>
                        {isLoading['whatsapp'] ? 'Analyzing...' : 'Analyze WhatsApp Chats'}
                    </button>
                    {error['whatsapp'] && <div className="alert alert-danger mt-2">{error['whatsapp']}</div >}
                    <ResultDisplay title="WhatsApp Analysis Result" data={data['whatsapp']} />
                </div>
                <hr />
                {/* Email */}
                <div className="mb-3">
                    <button className="btn btn-primary w-100" onClick={() => handleApiCall('email', triggerEmailScraping)} disabled={isLoading['email']}>
                        {isLoading['email'] ? 'Scraping...' : 'Scrape Emails'}
                    </button>
                    {error['email'] && <div className="alert alert-danger mt-2">{error['email']}</div >}
                    <ResultDisplay title="Email Scraper Result" data={data['email']} />
                </div>
                <hr />
                {/* Instagram */}
                <div className="mb-3">
                    <label htmlFor="instaUser" className="form-label">Instagram Username</label>
                    <div className="input-group">
                        <input
                            type="text"
                            className="form-control"
                            id="instaUser"
                            value={instaUsername}
                            onChange={(e) => setInstaUsername(e.target.value)}
                        />
                        <button className="btn btn-primary" onClick={() => handleApiCall('instagram', () => triggerInstagramScraping(instaUsername))} disabled={isLoading['instagram']}>
                            {isLoading['instagram'] ? 'Scraping...' : 'Scrape Instagram'}
                        </button>
                    </div>
                    {error['instagram'] && <div className="alert alert-danger mt-2">{error['instagram']}</div >}
                    <ResultDisplay title="Instagram Scraper Result" data={data['instagram']} />
                </div>
            </div>
        </div>
    );
};

export default ScrapingDashboard;
