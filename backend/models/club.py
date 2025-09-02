from pydantic import BaseModel
from typing import List, Dict, Optional

class ClubBase(BaseModel):
    name: str
    description: str

class ClubDataInput(BaseModel):
    clubs: List[ClubBase]

# New models for the ranked response
class RankedClub(BaseModel):
    rank: int
    name: str
    # The combined, normalized score from email and whatsapp activity
    total_engagement_score: float

class RankedCluster(BaseModel):
    cluster_id: int
    clubs: List[RankedClub]

class RankedClusteringResult(BaseModel):
    clusters: List[RankedCluster]
    outliers: List[str]