from typing import List
from fastapi import APIRouter
from fastapi import Response
from fastapi import status, Depends
from fastapi import HTTPException
from sqlalchemy import distinct, func
from .. import models, schemas, utils
from ..database import get_db, Session

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)

    new_user = models.User(
        **user.dict()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserPublicProfile)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()


    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id {id} not found")
    
    profile = db.query(
        models.User, 
        func.count(distinct(models.Post.id)).label("notes"),
        func.count(models.Vote.post_id).label("votes")
    ).join(
        models.Post, models.Post.owner_id == models.User.id, isouter=True
    ).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True
    ).group_by(
        models.User.id
    ).filter(
        models.User.id == id
    ).first()

    

    return profile