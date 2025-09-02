import pandas as pd
import numpy as np
import os

from models.club import ClubDataInput, RankedClusteringResult, RankedCluster, RankedClub
from utils.clubGrouper import AdvancedClubGrouper

def get_total_engagement_scores():
    """
    Generates a total engagement score for each club by combining WhatsApp and Email activity.
    """
    print("Calculating total engagement scores...")
    # --- 1. Load WhatsApp Data ---
    try:
        whatsapp_df = pd.read_csv("club_engagement_analysis.csv")
    except FileNotFoundError:
        print("Warning: club_engagement_analysis.csv not found. Skipping WhatsApp scores.")
        whatsapp_df = pd.DataFrame(columns=['Club', 'CEI'])

    # --- 2. Load and Process Email Data ---
    try:
        emails_df = pd.read_csv("2024_full_mails.csv")
        # Create a list of all known club names to check against
        # We get this from the whatsapp analysis file, as it's our primary source of club names
        all_club_names = whatsapp_df['Club'].unique()
        
        email_counts = {}
        for club_name in all_club_names:
            # Count emails where the sender contains the club name (case-insensitive)
            # This is a simple heuristic for attributing emails to clubs.
            try:
                count = emails_df[emails_df['Sender'].str.contains(club_name, case=False, na=False)].shape[0]
                email_counts[club_name] = count
            except Exception:
                email_counts[club_name] = 0 # Fallback if search fails
        email_df = pd.DataFrame(list(email_counts.items()), columns=['Club', 'EmailCount'])

    except FileNotFoundError:
        print("Warning: 2024_full_mails.csv not found. Skipping email scores.")
        email_df = pd.DataFrame(columns=['Club', 'EmailCount'])

    # --- 3. Merge Data ---
    # Start with a dataframe of all clubs we have whatsapp data for
    if 'Club' not in whatsapp_df.columns:
        return {}
        
    merged_df = pd.merge(whatsapp_df[['Club', 'CEI']], email_df, on='Club', how='left').fillna(0)

    # --- 4. Normalize Scores (0-1 range) ---
    # Normalize CEI (WhatsApp score)
    if not merged_df['CEI'].empty and merged_df['CEI'].max() != merged_df['CEI'].min():
        merged_df['whatsapp_norm'] = (merged_df['CEI'] - merged_df['CEI'].min()) / (merged_df['CEI'].max() - merged_df['CEI'].min())
    else:
        merged_df['whatsapp_norm'] = 0

    # Normalize Email Count
    if not merged_df['EmailCount'].empty and merged_df['EmailCount'].max() != merged_df['EmailCount'].min():
        merged_df['email_norm'] = (merged_df['EmailCount'] - merged_df['EmailCount'].min()) / (merged_df['EmailCount'].max() - merged_df['EmailCount'].min())
    else:
        merged_df['email_norm'] = 0

    # --- 5. Calculate Weighted Total Score ---
    merged_df['total_score'] = 0.6 * merged_df['whatsapp_norm'] + 0.4 * merged_df['email_norm']
    
    print("Engagement score calculation complete.")
    return pd.Series(merged_df.total_score.values, index=merged_df.Club).to_dict()


def run_clustering_and_ranking(club_data: ClubDataInput) -> RankedClusteringResult:
    """
    Takes club data, runs clustering, then ranks the clubs within each cluster.
    """
    # --- Step 1: Perform Clustering ---
    club_list_for_grouper = [club.model_dump() for club in club_data.clubs]
    grouper = AdvancedClubGrouper()
    grouped_clubs, outlier_clubs = grouper.group_clubs(club_list_for_grouper)

    # --- Step 2: Get Engagement Scores ---
    engagement_scores = get_total_engagement_scores()

    # --- Step 3: Rank clubs within each cluster ---
    ranked_clusters = []
    for cluster_id, club_names in grouped_clubs.items():
        # Create a list of tuples (club_name, score)
        club_scores = [(name, engagement_scores.get(name, 0)) for name in club_names]
        
        # Sort by score in descending order
        club_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create RankedClub objects
        ranked_clubs_list = [
            RankedClub(rank=i+1, name=name, total_engagement_score=score)
            for i, (name, score) in enumerate(club_scores)
        ]
        
        ranked_clusters.append(RankedCluster(cluster_id=cluster_id, clubs=ranked_clubs_list))

    return RankedClusteringResult(clusters=ranked_clusters, outliers=outlier_clubs)