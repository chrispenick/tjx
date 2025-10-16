from pydantic import BaseModel
class Quiz(BaseModel):
    season:str; vibe:str; palette:str; budget:float
