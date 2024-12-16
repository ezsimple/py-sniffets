import aiohttp
import asyncio
import requests

# 주의 : 버츄얼 호스트수(len(URLs))가 10을 넘으면 nginx.limit_req burst=10으로 인해 503 발생함.
HOST = "https://a1.mkeasy.kro.kr"
URIs = {
    "/health": "toy-project", # toy_project
    "/erp/health": "react-erp", # react-erp
    "/hr/health": "hr-server", # hr statistics
    "/quotes/health": "quotes", # famous sayings api
    "/chat/health": "chat", #  famous sayings ui
    "/past-weather/health": "past weather", # past weather
    "/v1/health": "http_auth", # personal file downloader
    "/auth/health": "keycloak", # keycloak
}

async def send_message(text):
    TOKEN = "5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc"
    CHAT_ID = "918743728"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,
        "text": text,
    }
    resp = requests.get(url, params=params)

    # Throw an exception if Telegram API fails
    resp.raise_for_status()

async def fetch_status(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            print(f"{url} is down! Status code: {response.status}")
            server = URIs[url] + 'is down!'
            await send_message(f"{server} is down! Status code: {response.status}")

async def check_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in urls]
        await asyncio.gather(*tasks)

async def main():
    urls_to_check = [f"{HOST}{uri}" for uri in URIs]  # Get URLs from dictionary keys
    await check_urls(urls_to_check)

asyncio.run(main())
