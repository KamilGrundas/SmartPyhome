import uvicorn
from fastapi import FastAPI


app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.include_router(views.router)
# app.include_router(pictures.router, prefix="/wizards")
# app.include_router(tags.router, prefix="/wizards")
# app.include_router(auth_new.router, prefix="/api")
 
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
