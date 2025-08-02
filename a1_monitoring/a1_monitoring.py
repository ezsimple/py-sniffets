# %%
import aiohttp
import asyncio
import requests
import subprocess

# 주의 : 버츄얼 호스트수(len(URLs))가 10을 넘으면 nginx.limit_req burst=10으로 인해 503 발생함.
HOST = "https://a1.mkeasy.kro.kr"
URIs = {
    "/health": "toy-project", # toy-project
    "/erp/health": "react-erp", # react-erp
    "/hr/health": "hr-server", # hr statistics
    "/quotes/health": "quotes", # famous sayings api
    "/chat/health": "chat", #  famous sayings ui
    "/past-weather/health": "past weather", # past weather
    "/v1/health": "http_auth", # personal file downloader
    "/auth/health": "keycloak", # keycloak
    "/calendar/health": "calendar api", # calendar api
}
async def check_nginx_status():
    try:
        # Nginx 상태 확인
        result = subprocess.run(['systemctl', 'is-active', 'nginx.service'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip() == 'active'
    except Exception as e:
        print(f"Error checking Nginx status: {e}")
        return False

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
    try:
        async with session.get(url) as response:
            if response.status != 200:
                msg = f"{url} is down! Status code: {response.status}"
                desc = URIs[url]
                service_name = list(URIs.keys())[list(URIs.values()).index(desc)]
                await send_message(f'{msg} ({service_name})')
    except aiohttp.ClientConnectorError:
        msg = f"Cannot connect to {url}"
        desc = URIs[url]
        service_name = list(URIs.keys())[list(URIs.values()).index(desc)]
        await send_message(f'{msg} ({service_name})')
    except Exception as e:
        msg = f"An error occurred while checking {url}: {e}"
        desc = URIs[url]
        service_name = list(URIs.keys())[list(URIs.values()).index(desc)]
        await send_message(f'{msg} ({service_name})')


async def check_urls(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in urls]
        await asyncio.gather(*tasks)

async def main():
    try:
        if not await check_nginx_status():
            msg = 'Nginx service is not running! Really?!'
            await send_message(f'{msg}')


        urls_to_check = [f"{HOST}{uri}" for uri in URIs]
        await check_urls(urls_to_check)

    except Exception as e:
        msg = '#오류# service is not running!'
        await send_message(f'{e}')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
