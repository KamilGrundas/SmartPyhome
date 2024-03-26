from prisma import Prisma
from prisma.models import Case_Price





async def add_case_record(body):
    db=Prisma()
    await db.connect()
    

    new_case_price = await db.case_price.create(
        data = {
            "name" : body.name,
            "price" : body.price
        }
    )

    await db.disconnect()

async def get_case_records():
    db=Prisma()
    await db.connect()
    all_case_records = await db.case_price.find_many()

    await db.disconnect()

    return all_case_records