import uvicorn
from fastapi import FastAPI
from prisma import Prisma
import asyncio

app = FastAPI()

@app.get("/")
async def list_posts():
    db = Prisma()
    await db.connect()

    posts = await db.post.find_many()

    await db.disconnect()

    return posts
 
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
