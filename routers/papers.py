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


router=APIRouter() 


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]
user_dependency= Annotated[dict , Depends(get_current_user)]


PAPERS=[]

class PaperRequest(BaseModel):
    #id : Optional[int]=Field(description='ID id not needed at create',default =None)
    title : str =Field(min_length=3,max_length=300)
    author : str =Field(min_length=3,max_length=200)
    abstract : str=Field(min_length=2,max_length=5000)
    year: int=Field(gt=1899)
    reading_status: str

    model_config =ConfigDict(  #needed to import ConfigDict from pydantic
        json_schema_extra= {
            "example":{
                "title": "Attention Is All You Need",
                "author": "Ashish Vaswani et al",
                "abstract": "Introduces the Transformer architecture, replacing recurrent neural networks with self-attention for sequence modeling tasks.",
                "year":2017,
                "reading_status":"Unread"
            }
        }
    )

 
#old : returning list 
#new : database, deleted old paper class and PAPERS list inside main

@router.get("/papers",status_code=status.HTTP_200_OK)
async def read_all_papers(user: user_dependency,db:db_dependency):
    return db.query(Paper).filter(Paper.owner_id==user.get('id')).all()

@router.get("/papers/{paper_id}",status_code=status.HTTP_200_OK)
async def read_paper(db:db_dependency, paper_id:int=Path(gt=0)):
    paper_model = db.query(Paper).filter(Paper.id==paper_id).first()
    if paper_model is not None:
        return paper_model

    raise HTTPException(status_code=404,detail='Paper not found')


@router.get("/papers/",status_code=status.HTTP_200_OK)
async def read_paper_by_year(db:db_dependency,paper_year:int=Query(gt=1899,lt=2026)):
    papers=db.query(Paper).filter(Paper.year==paper_year).all()

    if papers is not None:
        return papers

@router.get("/papers/status/")
async def read_status(db:db_dependency,reading_status:str):
    papers=db.query(Paper).filter(func.lower(Paper.reading_status)==reading_status.casefold()).all()

    if papers is not None:
        return papers 


@router.post("/add-paper",status_code=status.HTTP_201_CREATED)
async def add_paper(user : user_dependency, db:db_dependency,
                    paper_request:PaperRequest):

    if user is None:
        raise HTTPException(status_code=401,detail ="Authentication Failed")
    paper_model=Paper(**paper_request.model_dump(),owner_id=user.get('id'))
    
    db.add(paper_model)
    db.commit()
   

def find_paper_id(paper:Paper):
    paper.id =1 if len(PAPERS)==0 else PAPERS[-1].id+1
    return paper




@router.put("/papers/{paper_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_paper(db:db_dependency,
                      paper_request: PaperRequest,#PaperRequest needs to be above any path parameter
                       paper_id:int=Path(gt=0)):
    paper_model=db.query(Paper).filter(Paper.id==paper_id).first()
    
    if paper_model is None:
        raise HTTPException(status_code=404,detail='Paper not found')
    paper_model.title=paper_request.title
    paper_model.abstract=paper_request.abstract
    paper_model.author=paper_request.author
    paper_model.year=paper_request.year
    paper_model.reading_status=paper_request.reading_status

    db.add(paper_model)
    db.commit()

    
@router.delete("/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(db:db_dependency,paper_id:int=Path(gt=0)):
    paper_model = db.query(Paper).filter(Paper.id==paper_id).first()

    if paper_model is None:
        raise HTTPException(status_code=404,detail='Paper not found')
    db.query(Paper).filter(Paper.id==paper_id).delete()

    db.commit()