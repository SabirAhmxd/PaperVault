
from fastapi import FastAPI,Path,Query,HTTPException ,Depends
import models
from database import engine
from routers import auth,papers,admin


app=FastAPI()

models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(admin.router)

