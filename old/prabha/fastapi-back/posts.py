from typing import List

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
import models
import schema
from fastapi import APIRouter
from database import get_db
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer
import models
from database import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=os.getenv("tokenUrl"))

router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)



@router.get('/', response_model=List[schema.CreatePost])
def test_posts(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    post = db.query(models.Post).all()


    return  post

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=List[schema.CreatePost])
def test_posts_sent(post_post:schema.CreatePost, db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    new_post = models.Post(**post_post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return [new_post]


@router.get('/{id}', response_model=schema.CreatePost, status_code=status.HTTP_200_OK)
def get_test_one_post(id:int ,db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    idv_post = db.query(models.Post).filter(models.Post.id == id).first()

    if idv_post is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The id: {id} you requested for does not exist")
    return idv_post

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_test_post(id:int, db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    deleted_post = db.query(models.Post).filter(models.Post.id == id)


    if deleted_post.first() is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"The id: {id} you requested for does not exist")
    deleted_post.delete(synchronize_session=False)
    db.commit()



@router.put('/posts/{id}', response_model=schema.CreatePost)
def update_test_post(update_post:schema.PostBase, id:int, db:Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    updated_post =  db.query(models.Post).filter(models.Post.id == id)

    if updated_post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The id:{id} does not exist")
    updated_post.update(update_post.dict(), synchronize_session=False)
    db.commit()


    return  updated_post.first()