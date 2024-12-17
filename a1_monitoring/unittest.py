import asyncio
from a1_monitoring import send_message

@asyncio.coroutine
async def test_send_message():
    await send_message("hello")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_send_message())
