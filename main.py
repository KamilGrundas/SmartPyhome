import uvicorn
from fastapi import FastAPI, Depends
from src.database.models import User
from src.database.db import get_db
from src.repository import users
from sqlalchemy.orm import Session

app = FastAPI()


users.add_user(username="kamik", email="fajnymail", password="haslo", db=Depends(get_db))

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.include_router(views.router)
# app.include_router(pictures.router, prefix="/wizards")
# app.include_router(tags.router, prefix="/wizards")
# app.include_router(auth_new.router, prefix="/api")
 
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
