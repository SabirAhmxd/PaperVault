from fastapi import FastAPI,Path,Query,HTTPException
from pydantic import BaseModel,Field,ConfigDict
from typing import Optional
from starlette import status

import models
from database import engine



app=FastAPI() 

models.Base.metadata.create_all(bind=engine)

PAPERS=[]

class Paper:
    id:int
    title:str
    authors:str
    abstract:str
    year:int
    reading_status:str


    def __init__(self,id,title,author,abstract,year,reading_status):
        self.id=id
        self.title =title
        self.author = author
        self.abstract = abstract
        self.year = year
        self.reading_status=reading_status

class PaperRequest(BaseModel):
    id : Optional[int]=Field(description='ID id not needed at create',default =None)
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


PAPERS=[

    Paper(1,'Title One','Author 1','Cool Paper',2010,'Unread'),
    Paper(2,'Title Two','Author 2','Cool Paper',2010,'Completed'),
    Paper(3,'Title Three','Author 3','Cool Paper',2010,'Reading'),
    Paper(4,'Title Four','Author 4','Bad Paper',2014,'Unread'),
    Paper(5,'Title Five','Author 5','Decent Paper',2007,'Unread'),
    Paper(6,'Title One','Author 6','Cool Paper',2010,'Unread'),
]


@app.get("/papers",status_code=status.HTTP_200_OK)
async def read_all_papers():
    return PAPERS

@app.get("/papers/{paper_id}",status_code=status.HTTP_200_OK)
async def read_paper(paper_id:int=Path(gt=0)):
    for paper in PAPERS:
        if paper.id == paper_id:
            return paper
    raise HTTPException(status_code=404,detail='Item not found')


@app.get("/papers/",status_code=status.HTTP_200_OK)
async def read_paper_by_year(paper_year:int=Query(gt=1899,lt=2026)):
    papers_to_return =[]
    for paper in PAPERS:
        if paper.year==paper_year:
            papers_to_return.append(paper)
    return papers_to_return

@app.get("/papers/status/")
async def read_status(reading_status:str):
    papers_to_return=[]
    for paper in PAPERS:
        if paper.reading_status==reading_status:
            papers_to_return.append(paper)
    return papers_to_return


@app.post("/add-paper",status_code=status.HTTP_201_CREATED)
async def add_paper(paper_request:PaperRequest):
    new_paper=Paper(**paper_request.model_dump())
    PAPERS.append(find_paper_id(new_paper))

def find_paper_id(paper:Paper):
    paper.id =1 if len(PAPERS)==0 else PAPERS[-1].id+1
    return paper




@app.put("/papers/update_paper",status_code=status.HTTP_204_NO_CONTENT)
async def update_paper(paper: PaperRequest):
    paper_changed=False
    for i in range(len(PAPERS)):
        if PAPERS[i].id==paper.id:
            PAPERS[i]=paper
            paper_changed=True
    if not paper_changed:
        raise HTTPException(status_code=404,detail='Item not found')



    
@app.delete("/papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_paper(paper_id:int=Path(gt=0)):
    paper_deleted=False
    for i in range(len(PAPERS)):
        if PAPERS[i].id ==paper_id:
            PAPERS.pop(i)
            paper_deleted=True
            break
    if not paper_deleted:
        raise HTTPException(status_code=404,detail='Item not found')
    
