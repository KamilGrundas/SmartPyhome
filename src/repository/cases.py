from prisma import Prisma






async def add_case_record(body):
    db=Prisma()
    print(body)
    