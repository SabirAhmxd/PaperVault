from typing import Annotated
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter,Path,Query,HTTPException ,Depends
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from starlette import status
from models import Paper
from database import SessionLocal
from .auth import get_current_user


router=APIRouter(prefix = '/admin',tags=['admin']) 


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency= Annotated[dict , Depends(get_current_user)]

@router.get("/paper",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')
    return db.query(Paper).all()


@router.delete('/paper/{paper_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(user:user_dependency,db:db_dependency, paper_id:int=Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail='Authentication Failed')
    paper_model = db.query(Paper).filter(Paper.id==paper_id).first()
    if paper_model is None:
        raise HTTPException(status_code=404, detail='Paper Not Found')
    db.query(Paper).filter(Paper.id==paper_id).delete()

    db.commit()