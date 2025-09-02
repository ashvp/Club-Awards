const API_BASE_URL = 'http://127.0.0.1:8000';

// A generic, reusable fetch function with proper error handling
async function apiFetch(endpoint: string, options: RequestInit = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred with the API request.' }));
            throw new Error(errorData.detail || 'API request failed');
        }
        // Handle responses that don't have a body (e.g., 204 No Content)
        if (response.status === 204) {
            return null;
        }
        return response.json();
    } catch (error) {
        // Catch network errors
        console.error("Network or API call error:", error);
        throw error;
    }
}

// --- Scraping Endpoint Calls ---
export const triggerEmailScraping = () => apiFetch('/scraping/emails', { method: 'POST' });
export const triggerWhatsappAnalysis = () => apiFetch('/scraping/whatsapp', { method: 'POST' });
export const triggerInstagramScraping = (username: string) => apiFetch(`/scraping/instagram/${username}`, { method: 'POST' });

// --- Clustering Endpoint Call ---
export interface Club {
    name: string;
    description: string;
}

export interface ClubDataInput {
    clubs: Club[];
}

export const groupClubs = (clubData: ClubDataInput) => {
    return apiFetch('/clustering/group-clubs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(club_data),
    });
};
