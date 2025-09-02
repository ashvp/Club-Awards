import React, { useState } from 'react';
import { groupClubs, Club } from '../services/api';

// Define the structure of the API response for type safety
interface RankedClub {
    rank: number;
    name: string;
    total_engagement_score: number;
}

interface RankedCluster {
    cluster_id: number;
    clubs: RankedClub[];
}

interface ClusteringResult {
    clusters: RankedCluster[];
    outliers: string[];
}

const sampleClubData: Club[] = [
    {'name': 'Rhythm', 'description': "Rhythm is SNUC's very own dance club which aims to provide a space for students, regardless of prior experience to explore the various forms of dance and to use dance as a mode of expression. They have also set a target to represent our university in various competitions and events, all the while hosting workshops and choreography sessions for its members."},
    {'name': 'Capturesque', 'description': "CAPTURESQUE is a platform created to bring students of the same creative interest closer to seeing the world through a lens.They intend to be the designated photographer for university events, conduct learning sessions and represent our university in photography competitions."},
    {'name': 'Omnia', 'description': "The Omnia club is a vibrant hub on campus dedicated to protecting animals, fostering inclusivity for the LGBTQ+ community, and championing environmental preservation. With a passion for advocacy and activism, we unite to create a safe and supportive space for all beings. Join us in our mission to cultivate compassion, celebrate diversity, and safeguard our planet for generations to come. Embrace the power of unity and change with Omnia – where every voice is heard, and every action counts. Together, we aim to make a meaningful difference in the world around us."},
    {'name': 'Atwas', 'description': "All The World's A Stage(ATWAS) intends to set up the stage, pull back the curtains, and introduce the world of theatre to SNUC. They have plans to teach and develop every aspect of theatre from acting to lighting and involve the members in activities such as studying famous plays to help mature their skills."},
    {'name': 'Ameya', 'description': "We are an expressive club of trained and passionate dancers who always strive to bring our best to the stage. Our motto “yatho bhaava: thatho rasa:”, is a Sanskrit shloka meaning where there is feeling and emotion, there arises expression' emphasizes the importance of conveying emotions through dance. We have performed in various university events, including Women's Day, Republic Day, Freshers' Day, and many more, where our captivated audience are often tapping their feet to our beats. We also kicked off Instincts ‘23, one of the biggest campus cultural fests, with our inaugural performance and showcased our talent in Choreonite portraying the theme “The Wonders of Lord Krishna”. From enrapturing solos to beautifully coordinated group performances, Ameya has done it all. Our online competition “A Jathi with a twist” showcased the creativity of our club members and uncovered new talent. Ameya always aims to bring something fresh and unparalleled to the stage while embracing the roots of our culture"},
];

const ClusteringInterface: React.FC = () => {
    const [jsonInput, setJsonInput] = useState(JSON.stringify({ clubs: sampleClubData }, null, 2));
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ClusteringResult | null>(null);

    const handleCluster = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const clubData = JSON.parse(jsonInput);
            const response = await groupClubs(clubData);
            setResult(response);
        } catch (err: any) {
            setError('Invalid JSON or API Error: ' + err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card h-100">
            <div className="card-header">
                <h3>Club Clustering & Ranking Tool</h3>
            </div>
            <div className="card-body">
                <div className="mb-3">
                    <label htmlFor="clubDataJson" className="form-label">Club Data (JSON format)</label>
                    <textarea
                        className="form-control"
                        id="clubDataJson"
                        rows={8}
                        value={jsonInput}
                        onChange={(e) => setJsonInput(e.target.value)}
                    />
                </div>
                <button className="btn btn-success w-100" onClick={handleCluster} disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Group and Rank Clubs'}
                </button>
                {error && <div className="alert alert-danger mt-2">{error}</div>}
                {result && (
                    <div className="mt-3">
                        <h4 className="mb-3">Results</h4>
                        <h5>Clusters</h5>
                        {result.clusters.length > 0 ? result.clusters.map((cluster) => (
                            <div key={cluster.cluster_id} className="mb-3 card bg-light">
                                <div className="card-body">
                                    <h6 className="card-title">Cluster {cluster.cluster_id + 1}</h6>
                                    <ul className="list-group list-group-flush">
                                        {cluster.clubs.map((club) => 
                                            <li key={club.name} className="list-group-item d-flex justify-content-between align-items-center">
                                                <span>
                                                    <span className="badge bg-primary rounded-pill me-2">{club.rank}</span>
                                                    {club.name}
                                                </span>
                                                <span className="badge bg-secondary">Score: {club.total_engagement_score.toFixed(3)}</span>
                                            </li>
                                        )}
                                    </ul>
                                </div>
                            </div>
                        )) : <p>No clusters were formed.</p>}
                        
                        <h5 className="mt-4">Outliers</h5>
                        {result.outliers.length > 0 ? (
                            <ul className="list-group">
                                {result.outliers.map((club: string) => <li key={club} className="list-group-item">{club}</li>)}
                            </ul>
                        ) : <p>No outliers found.</p>}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ClusteringInterface;