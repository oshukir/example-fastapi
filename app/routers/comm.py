from typing import List, Optional
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Depends, status
from .. import models, schemas, oauth2
from ..database import Session, get_db

router = APIRouter(
    prefix="/comments",
    tags=['Comments']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentOut)
def create_comment(comment: schemas.CommentBase, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    post_query_result = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post_query_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {comment.post_id} is not found")
    
    if current_user.id != post_query_result.owner_id and post_query_result.is_private == True:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"post with id {post_query_result.id} is private")
    
    new_comment = models.Comment(
        **comment.dict(),
        owner_id = current_user.id,   
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

@router.get("/{id}", response_model=schemas.CommentOut)
def get_comments(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with ID {id} was not found")
    
    return comment
    

@router.put("/{id}", response_model=schemas.CommentOut)
def update_comment(id: int, comm: schemas.CommentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    query = db.query(models.Comment).where(models.Comment.id == id)
    comment = query.first()
    print(comment)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id {id} not found")
    

    if comment.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"not authorised to perform request to action")
    

    query.update(comm.dict(), synchronize_session=False)
    db.commit()

    return comment



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    query = db.query(models.Comment).where(models.Comment.id == id)
    comment = query.first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Comment with id {id} not found")
    
    post = db.query(models.Post).where(models.Post.id == comment.post_id).first()
    
    if comment.owner_id != current_user.id and current_user.id != post.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"not authorised to perform request to action")
    
    query.delete(synchronize_session=False)
    db.commit()
    