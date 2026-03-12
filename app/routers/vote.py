from fastapi import Depends, APIRouter, status, HTTPException
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote: schemas.Vote_Create, db: Session = Depends(get_db), 
                current_user: models.User = Depends(oauth2.get_current_user)):
    
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {vote.post_id} not found")
    
    
    vote_request = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_request.first()


    if (vote.dir == True):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="post has already been voted")
        else:
            new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)
            db.add(new_vote)
            db.commit()
            return {
                "message" : "successefully added vote"
            }
        
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Vote doesnt exist")
        
        else:
            vote_request.delete()
            db.commit()

            return {
                "message" : "successfully deleted vote"
            }