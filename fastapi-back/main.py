from typing import Union, Annotated
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
import posts.models
from posts.database import engine, Base
import posts.posts
import posts.schema
import slack.slack

app = FastAPI()

# posts

posts.models.Base.metadata.create_all(bind=engine)
app.include_router(posts.posts.router)

# slack
app.include_router(slack.slack.router)


