from typing import List, Optional
from fastapi import APIRouter
from fastapi import Response
from fastapi import status, Depends
from fastapi import HTTPException
from sqlalchemy import func
from .. import models, schemas, utils, oauth2
from ..database import get_db, Session

router = APIRouter(
    prefix='/posts',
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOUT])
def get_posts(db: Session = Depends(get_db), 
              current_user: models.User = Depends(oauth2.get_current_user), 
              limit: int = 10, skip: int = 0, search: Optional[str] = ""): 

    # Обязательно используем .label("votes"), чтобы Pydantic знал, куда положить число
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostReturn)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    new_post = models.Post(
        **post.dict(),
        owner_id = current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/latest", response_model=schemas.PostReturn)
def get_latest_post(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return post

@router.get("/{id}", response_model=schemas.PostReturn)
def get_posts(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail=f"not authorised to perform request")
    
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"not authorised to perform request to action")
    
    post_query.delete()
    db.commit()

    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostReturn)
def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id {id} not found")
    
    post = post_query.first()
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"not authorised to perform request to action")
    
    post_query.update(updated_post.dict())
    db.commit()

    return post_query.first()