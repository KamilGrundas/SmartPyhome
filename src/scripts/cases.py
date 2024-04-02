from time import sleep
from src.repository.cases import add_case_record
from src.schemas import Case_Price_Model
import asyncio
import aiohttp

def urlizer(name):
    result = name.replace(" ", "%20").replace("&", "%26")
    return result


def valuizer(value):
    result = value.replace(",", ".").replace("zł", "")
    return float(result)


cases = ("CS20 Case",
    "Chroma 2 Case",
    "Chroma 3 Case",
    "Chroma Case",
    "Clutch Case",
    "Danger Zone Case",
    "Falchion Case",
    "Fracture Case",
    "Gamma 2 Case",
    "Gamma Case",
    "Glove Case",
    "Horizon Case",
    "Operation Breakout Weapon Case",
    "Operation Wildfire Case",
    "Prisma 2 Case",
    "Prisma Case",
    "Revolver Case",
    "Shadow Case",
    "Shattered Web Case",
    "Snakebite Case",
    "Spectrum 2 Case",
    "Spectrum Case",
    "Operation Broken Fang Case",
    "Dreams & Nightmares Case",
    "Revolution Case",
    "Recoil Case")



url_core = "https://steamcommunity.com/market/priceoverview/?appid=730&currency=6&market_hash_name="

async def fetch_case_data(session, url):
    async with session.get(url) as response:
        return await response.json()

async def get_case_prices():
    async with aiohttp.ClientSession() as session:
        for case in cases:
            url = url_core + urlizer(case)
            response = await fetch_case_data(session, url)
            await asyncio.sleep(3)  # Oczekiwanie 3 sekundy między zapytaniami

            lowest_price = response["lowest_price"]
            case = Case_Price_Model(name=case, price=round(valuizer(lowest_price), 2))
            await add_case_record(case)


#  items = {
#     "CS20 Case": 980,
#     "Chroma 2 Case": 169,
#     "Chroma 3 Case": 1,
#     "Chroma Case": 4,
#     "Clutch Case": 24,
#     "Danger Zone Case": 94,
#     "Falchion Case": 8,
#     "Fracture Case": 4,
#     "Gamma 2 Case": 240,
#     "Gamma Case": 3,
#     "Glove Case": 14,
#     "Horizon Case": 7,
#     "Operation Breakout Weapon Case": 22,
#     "Operation Wildfire Case": 9,
#     "Prisma 2 Case": 4,
#     "Prisma Case": 5,
#     "Revolver Case": 6,
#     "Shadow Case": 15,
#     "Shattered Web Case": 4,
#     "Snakebite Case": 221,
#     "Spectrum 2 Case": 21,
#     "Spectrum Case": 4,
#     "Operation Broken Fang Case": 50,
#     "Dreams & Nightmares Case": 2,
#     "Revolution Case": 3,
#     "Recoil Case": 4,
# }       


