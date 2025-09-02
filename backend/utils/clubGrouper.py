from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class AdvancedClubGrouper:
    def __init__(self):
        print("Loading sentence transformer model (may download on first run)...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.clusterer = AgglomerativeClustering(
            n_clusters=None,
            metric='cosine',
            linkage='average'
        )

    def _find_optimal_threshold(self, embeddings):
        """
        Finds an optimal distance threshold using a simple statistical measure
        that is more robust for small datasets.
        """
        k = 3
        print(f"Finding optimal distance threshold using k={k} nearest neighbors...")

        nbrs = NearestNeighbors(n_neighbors=k, metric='cosine').fit(embeddings)
        distances, _ = nbrs.kneighbors(embeddings)
        
        # Get the distance to the nearest neighbor for each point
        nearest_neighbor_dists = np.sort(distances[:, 1])

        # For small datasets, the knee-finding can be unstable.
        # Using the median of the nearest neighbor distances is a more robust heuristic.
        median_dist = np.median(nearest_neighbor_dists)
        
        # Set the threshold to be slightly higher than the median to encourage grouping
        optimal_threshold = median_dist * 1.2 # Increased multiplier slightly for broader clusters

        print(f"Automatically determined optimal distance threshold: {optimal_threshold:.4f}")
        return optimal_threshold

    def group_clubs(self, club_data):
        if not club_data or len(club_data) < 2:
            print("Not enough club data to perform clustering.")
            return {}, [club['name'] for club in club_data]

        names = [club['name'] for club in club_data]
        descriptions = [club['description'] for club in club_data]

        # --- Step 1: Summarize descriptions using TF-IDF to extract keywords ---
        print("\nStep 1: Summarizing descriptions into keywords using TF-IDF...")
        summaries = []
        try:
            # Use TF-IDF to find important words, ignoring common English stop words
            # and words that are too frequent (max_df) or too rare (min_df).
            vectorizer = TfidfVectorizer(stop_words='english', max_df=0.85, min_df=2, max_features=1000)
            tfidf_matrix = vectorizer.fit_transform(descriptions)
            feature_names = np.array(vectorizer.get_feature_names_out())
            
            for i in range(tfidf_matrix.shape[0]):
                doc_scores = tfidf_matrix[i].toarray().flatten()
                # Get the indices of the top 10 keywords
                top_indices = doc_scores.argsort()[-10:]
                # Filter out keywords with a score of 0
                top_indices = [idx for idx in top_indices if doc_scores[idx] > 0]
                top_keywords = feature_names[top_indices]
                summaries.append(" ".join(top_keywords))
        except ValueError:
            # This can happen if the vocabulary is too small after filtering.
            print("TF-IDF produced an empty vocabulary. Using raw descriptions as fallback.")
            summaries = descriptions

        print("\nGenerated Summaries (Keywords):")
        for i in range(len(names)):
            print(f"- {names[i]}: {summaries[i]}")

        # --- Step 2: Encode the keyword-based summaries ---
        print("\nStep 2: Encoding summarized descriptions into semantic vectors...")
        embeddings = self.model.encode(summaries, show_progress_bar=True)

        # --- Step 3: Find the optimal clustering threshold ---
        optimal_threshold = self._find_optimal_threshold(embeddings)
        
        # --- Step 4: Run Clustering ---
        print(f"\nStep 4: Running Agglomerative Clustering with threshold={optimal_threshold:.4f}...")
        self.clusterer.set_params(distance_threshold=optimal_threshold)
        self.clusterer.fit(embeddings)
    
        labels = self.clusterer.labels_
        
        temp_clusters = {}
        for i, label in enumerate(labels):
            if label not in temp_clusters:
                temp_clusters[label] = []
            temp_clusters[label].append(names[i])

        clusters = {}
        outliers = []
        for clubs in temp_clusters.values():
            if len(clubs) <= 1:
                outliers.extend(clubs)
            else:
                clusters[len(clusters)] = clubs

        print("\nClustering complete.")
        return clusters, outliers


if __name__ == '__main__':
    # This sample data will not be modified, as requested.
    # The processing happens inside the group_clubs function.
    sample_club_data = [
        {'name': 'Rhythm', 'description': "Rhythm is SNUC's very own dance club which aims to provide a space for students, regardless of prior experience to explore the various forms of dance and to use dance as a mode of expression. They have also set a target to represent our university in various competitions and events, all the while hosting workshops and choreography sessions for its members."},
        {'name': 'Capturesque', 'description': "CAPTURESQUE is a platform created to bring students of the same creative interest closer to seeing the world through a lens.They intend to be the designated photographer for university events, conduct learning sessions and represent our university in photography competitions."},
        {'name': 'Omnia', 'description': "The Omnia club is a vibrant hub on campus dedicated to protecting animals, fostering inclusivity for the LGBTQ+ community, and championing environmental preservation. With a passion for advocacy and activism, we unite to create a safe and supportive space for all beings. Join us in our mission to cultivate compassion, celebrate diversity, and safeguard our planet for generations to come. Embrace the power of unity and change with Omnia – where every voice is heard, and every action counts. Together, we aim to make a meaningful difference in the world around us."},
        {'name': 'Atwas', 'description': "All The World's A Stage(ATWAS) intends to set up the stage, pull back the curtains, and introduce the world of theatre to SNUC. They have plans to teach and develop every aspect of theatre from acting to lighting and involve the members in activities such as studying famous plays to help mature their skills."},
        {'name': 'Ameya', 'description': "We are an expressive club of trained and passionate dancers who always strive to bring our best to the stage. Our motto “yatho bhaava: thatho rasa:”, is a Sanskrit shloka meaning where there is feeling and emotion, there arises expression' emphasizes the importance of conveying emotions through dance. We have performed in various university events, including Women's Day, Republic Day, Freshers' Day, and many more, where our captivated audience are often tapping their feet to our beats. We also kicked off Instincts ‘23, one of the biggest campus cultural fests, with our inaugural performance and showcased our talent in Choreonite portraying the theme “The Wonders of Lord Krishna”. From enrapturing solos to beautifully coordinated group performances, Ameya has done it all. Our online competition “A Jathi with a twist” showcased the creativity of our club members and uncovered new talent. Ameya always aims to bring something fresh and unparalleled to the stage while embracing the roots of our culture"},
        {'name': 'SNUMUN Society', 'description': "SNUMUN Society aims towards shaping today's youth into tomorrow's leaders. Refined critical thinking, public speaking, listening, teamwork and problem-solving skills are the areas the club will focus on. It plans to participate in various MUNs and organize SNUC's MUN. The club is open to both new and experienced students and is all set towards its inception."},
        {'name': 'Potential', 'description': "POTENTIAL has been established to help students get a head start in the field of Robotics. They plan to encourage a start-up culture within the university, help the members be industry-ready with significant technical growth in Arduino, Raspberry Pi, and support student projects."},
        {'name': 'Montage', 'description': 'This club is a platform for all budding filmmakers, critiques and movie enthusiasts. We aim to provide a space to help nurture creativity and audio-visually showcase the world through our lens. We will be organising workshops with experts in the mass media industry as well as competitions to accentuate socio-economic issues.'},
        {'name': 'Coding Club', 'description': "Coding Club is for everyone, regardless of their current level of knowledge. We all have the right to learn, and we believe learning is more fun and efficient when we help each other along the way. The club not only focuses on coding but also on logical, analytical and problem-solving skills. The Coding Club aims to establish a coding culture on campus, reaching every student passionate about coding."},
        {'name': 'Quiz Club', 'description': "COGNITION's goals are to introduce and get students pumped up about quizzing. They plan on doing this by using their platform to host multiple types of events like workshops and quizzes with different categories of questions to make their members all-rounders. With this, they also hope to bring home laurels to the university for both competing and conducting events."},
        {'name': 'Voice Out', 'description': "VOICE OUT serves as a platform for the students to express their views without any fear. The name itself is a voice out which is to voice out one's opinions. It aims to bring out the orating skills one has lying deep down inside him/her."},
        {'name': 'Isai', 'description': "ISAI, the music club of SNUC unites the many voices of its members into the universal language of music. They plan to use its platform to help the students express their creativity and talent through various events. As well, to bring laurels to the university from participating in individual and Band Competitions."},
        {'name': 'Business Club', 'description': "BUSINESS CLUB aims to provide an all-inclusive platform for students from all academic backgrounds to freely explore multiple trending topics in the realm of business as per their interests and preferences."},
        {'name': 'Handila', 'description': "HANDILA SNUC's very own art club platform for art enthusiasts to show their artistic insights. They are coming up with lots of events starting from themed decoration to half-yearly exhibitions. They are also planning to participate in lots of events and bring laurels to the university."},
        {'name': 'Lingua', 'description': "The English Literature club has been conceived to provide a platform for students to display their skills in the diverse arena of English literature. We have a cornucopia of events planned such as oratory, debates, open mics, book clubs and plays and are excited to welcome all those who are interested. So bring out the bibliophile in you and hop on this journey together."},
        {'name': 'Checkmate', 'description': "CHECKMATE is the chess club at SNUC which is a space for enthusiasts of the game, experienced players and beginners alike. Their goal is to hold activities and events to encourage the students to use their wits and tactics through chess. They also aim at representing the university by participating in both online and offline tournaments."},
        {'name': 'TEDx', 'description': "TED club looks forward to supporting its members in discovering, researching, exploring and presenting their big ideas in the form of short, TED-style talks. The club plans on bringing well established TED speakers and TED fellows including educators, designers, animators, screenwriters, directors, academic researchers, science writers, historians, journalists and editors"}
    ]

    # sample_club_data = []
    # with open("clubs_paragraph.txt") as file:
    #     for line in file:


    print("--- Grouping Clubs with Advanced Method (Keywords + Agglomerative Clustering) ---")
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
