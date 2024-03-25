import uvicorn
from fastapi import FastAPI
from prisma import Prisma
from src.routes import cases

app = FastAPI()

app.include_router(cases.router, prefix="/")

@app.get("/")
async def list_posts():
    db = Prisma()
    await db.connect()

    posts = await db.post.find_many()

    await db.disconnect()

    return posts

@app.post("/post-something/")
async def add_post():
    db=Prisma()
    await db.connect()

    new_post = await db.case.create(
        data ={
            "title" : "Tytuł",
            "content" : "Kontent",
            "published" : True
        }
    )

    await db.disconnect()
 
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
