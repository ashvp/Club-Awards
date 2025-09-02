
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import numpy as np

class AdvancedClubGrouper:
    def __init__(self):
        print("Loading sentence transformer model (may download on first run)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dbscan = DBSCAN(eps=1.1, min_samples=2)
        # 1.1 is the best for now
    def group_clubs(self, club_data):
        if not club_data:
            return {}, []

        names = [club['name'] for club in club_data]
        descriptions = [club['description'] for club in club_data]

        print("Encoding descriptions into semantic vectors...")
        embeddings = self.model.encode(descriptions, show_progress_bar=True)

        print("Running DBSCAN clustering...")
        self.dbscan.fit(embeddings)
    
        labels = self.dbscan.labels_
        
        clusters = {}
        outliers = []
        
        for i, label in enumerate(labels):
            if label == -1:
                outliers.append(names[i])
                continue
            
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(names[i])

        print("Clustering complete.")
        return clusters, outliers


if __name__ == '__main__':
    sample_club_data = [
        {'name': 'SNU Coderz', 'description': 'A club for competitive programming, algorithms, and data structures. We solve problems and participate in coding contests.'},
        {'name': 'Data Science Society', 'description': 'Exploring the world of data analysis, machine learning, and artificial intelligence. We work on projects with real-world datasets.'},
        {'name': 'The Finance & Investment Club', 'description': 'Dedicated to understanding financial markets, investment strategies, and economic trends. We analyze stocks and market data.'},
        {'name': 'Robotics Club', 'description': 'We design, build, and program robots for various competitions. Focus on hardware, electronics, and control systems.'},
        {'name': 'Market Watchers', 'description': 'An association for students interested in stock market analysis, trading, and financial modeling.'},
        {'name': 'AI Innovators', 'description': 'A community for learning and applying artificial intelligence and deep learning techniques to solve complex challenges.'},
        {'name': 'Hardware Hackers', 'description': 'For enthusiasts of electronics, microcontrollers, and building physical computing projects from scratch.'},
        {'name': 'Ameya', 'description': 'A club dedicated to the practice and performance of classical Indian dance forms.'},
        {'name': 'Rhythm is Dance', 'description': 'A vibrant community for all dance enthusiasts, exploring styles from hip-hop to contemporary.'},
        {'name': 'Atwas', 'description': 'The theatre society for acting, directing, and stage production. We put on plays and workshops.'},
        {'name': 'Montage', 'description': 'The film club for movie lovers. We watch, discuss, and create short films and cinematic analyses.'}
    ]

    print("--- Grouping Clubs with Advanced Method (Embeddings + DBSCAN) ---")
    grouper = AdvancedClubGrouper()
    grouped_clubs, outlier_clubs = grouper.group_clubs(sample_club_data)

    
    cluster_id_counter = 1
    for cluster_label, clubs in grouped_clubs.items():
        print(f"\n--- Auto-Discovered Cluster {cluster_id_counter} ---")
        for club_name in clubs:
            print(f"- {club_name}")
        cluster_id_counter += 1
        
    if outlier_clubs:
        print("\n--- Outlier Clubs (did not fit into a group) ---")
        for club_name in outlier_clubs:
            print(f"- {club_name}")
