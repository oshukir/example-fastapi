from typing import List, Literal, Optional
from fastapi import APIRouter
from fastapi import Response
from fastapi import status, Depends
from fastapi import HTTPException
from sqlalchemy import distinct, func
from .. import models, schemas, oauth2
from ..database import get_db, Session

router = APIRouter(
    prefix='/posts',
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOUT])
def get_posts(db: Session = Depends(get_db), 
              current_user: models.User = Depends(oauth2.get_current_user), 
              limit: int = 10, skip: int = 0, search: Optional[str] = "",
              sort: Optional[Literal["latest", "popular"]] = "latest"): 

    # Обязательно используем .label("votes"), чтобы Pydantic знал, куда положить число
    if sort == "latest":
        results = db.query(models.Post, func.count(distinct(models.Vote.post_id)).label("votes"), 
                        func.count(distinct(models.Comment.post_id)).label("comms")).join(
                        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).join(
                        models.Comment, models.Comment.post_id == models.Post.id, isouter=True).group_by(
                        models.Post.id).filter(models.Post.title.contains(search)).order_by(models.Post.created_at.desc()).limit(
                        limit).offset(skip).all()
    else:
        results = db.query(models.Post, func.count(distinct(models.Vote.post_id)).label("votes"), 
                        func.count(distinct(models.Comment.post_id)).label("comms")).join(
                        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).join(
                        models.Comment, models.Comment.post_id == models.Post.id, isouter=True).group_by(
                        models.Post.id).filter(models.Post.title.contains(search)).order_by(
                        func.count(distinct(models.Vote.post_id)).desc()).limit(limit).offset(skip).all()

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

@router.get("/{id}", response_model=schemas.PostOUT)
def get_posts(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes"), 
                    func.count(models.Comment.post_id).label("comms")).join(
                    models.Vote, models.Vote.post_id == models.Post.id, isouter=True).join(
                    models.Comment, models.Comment.post_id == models.Post.id, isouter=True).group_by(
                    models.Post.id).filter(models.Post.id == id).first()

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

@router.get("/{id}/comments", response_model=List[schemas.CommentOut])
def get_post_comments(
    id: int,
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} not found"
        )
    
    comments = db.query(models.Comment).filter(
        models.Comment.post_id == id,
        models.Comment.content.contains(search)
    ).limit(limit).offset(skip).all()

    return comments