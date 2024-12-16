import aiohttp
import asyncio

# 주의 : 버츄얼 호스트수(len(URLs))가 10을 넘으면 nginx.limit_req burst=10으로 인해 503 발생함.
HOST = "https://a1.mkeasy.kro.kr"
URIs = [
    "/health", # toy_project
    "/erp/health", # react-erp
    "/hr/health", # hr statistics
    "/quotes/health", # famous sayings api
    "/chat/health", #  famous sayings ui
    "/past-weather/health", # past weather
    "/v1/health", # personal file downloader
    "/auth/health", # keycloak
]

async def fetch_status(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            print(f"{url} is down! Status code: {response.status}")

async def check_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in urls]
        await asyncio.gather(*tasks)

async def main():
    urls_to_check = [f"{HOST}{uri}" for uri in URIs]
    await check_urls(urls_to_check)

asyncio.run(main())
