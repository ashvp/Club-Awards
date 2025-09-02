from fastapi import APIRouter
from models.club import ClubDataInput, RankedClusteringResult # Updated model
from services.clustering_service import run_clustering_and_ranking # Updated service function

router = APIRouter(
    prefix="/clustering",
    tags=["Clustering"],
)

@router.post("/group-clubs", response_model=RankedClusteringResult) # Updated response model
def group_clubs_endpoint(club_data: ClubDataInput):
    """
    Accepts a list of club names and descriptions, groups them by similarity,
    and ranks the clubs within each group based on a combined engagement score.
    """
    return run_clustering_and_ranking(club_data)