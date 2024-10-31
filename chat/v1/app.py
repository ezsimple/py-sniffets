import json
import uuid
import httpx
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Cookie
import paho.mqtt.client as mqtt
import asyncio
from kakaotrans import Translator
from datetime import datetime
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
import logging
import os
from cryptography.fernet import Fernet

load_dotenv()
PREFIX="/chat" 
WS_SERVER = os.getenv("WS_SERVER", f'ws://localhost:4444{PREFIX}/ws')

# 암호화 키 생성 (실제 애플리케이션에서는 안전한 방법으로 관리해야 함)
SECRET_KEY = os.getenv("SECRET_KEY", Fernet.generate_key())
cipher = Fernet(SECRET_KEY)

# 로깅 설정
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)  # log 디렉토리가 없으면 생성

current_date = datetime.now().strftime("%Y-%m-%d")
log_file_name = f"app-{current_date}.log"
log_file_path = os.path.join(log_dir, log_file_name)

handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1, backupCount=7)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(filename)s - line:%(lineno)d - %(message)s'))

logging.basicConfig(
    level=logging.WARNING, # 기본 로킹레벨을 WARNING로
    handlers=[
        handler,
        logging.StreamHandler()  # 콘솔에도 로그 출력
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # 현재 파일만 디버그 레벨로 설정

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix=PREFIX)
logger.info(f"WS_SERVER : {WS_SERVER}")

mqtt_broker = "127.0.0.1"
mqtt_client = mqtt.Client()

# WebSocket 연결 관리
clients = {}

# MQTT 메시지 수신 콜백
def on_message(client, userdata, message):
    message_data = json.loads(message.payload.decode())
    user_id = message_data.get('user_id')
    
    if user_id in clients:
        asyncio.run(send_message_to_clients(message_data, user_id))

mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker)
mqtt_client.loop_start()  # MQTT 클라이언트 시작

async def send_message_to_clients(message_data, user_id):
    client = clients[user_id]['websocket']
    try:
        await client.send_json(message_data)
    except Exception as e:
        logger.error(f"Error sending message to client: {e}")

async def get_random_quote():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            return response.json()
        return {"content": "격언을 가져오는 데 실패했습니다.", "author": "알 수 없음"}

async def translate_quote(quote):
    translator = Translator()
    loop = asyncio.get_event_loop()
    translated_text = await loop.run_in_executor(None, translator.translate, quote['q'], 'en', 'kr')
    return translated_text

@router.get("/")
async def get(request: Request, user_id: str = Cookie(None)):

    timestamp = datetime.now().timestamp()  # 현재 시간을 타임스탬프로 변환
    response = templates.TemplateResponse("chat.html", {"request": request, "timestamp": timestamp, "WS_SERVER": WS_SERVER})

    if user_id is None:
        user_id = str(uuid.uuid4())
        encrypted_user_id = cipher.encrypt(user_id.encode()).decode()
        response.set_cookie(key="user_id", value=encrypted_user_id)  # 쿠키에 user_id 저장

    return response

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = Cookie(None)):
    if user_id is None:
        raise HTTPException(status_code=403, detail="User ID not provided")

    try:
        user_id = cipher.decrypt(user_id.encode()).decode()  # 복호화
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise HTTPException(status_code=400, detail="Invalid user ID")

    mqtt_topic = f"chat/messages/{user_id}"  # 사용자별 MQTT 토픽 생성
    mqtt_client.subscribe(mqtt_topic)  # 사용자별 MQTT 토픽 구독
    logger.debug(f"Subscribed to MQTT topic: {mqtt_topic}")

    await websocket.accept()
    clients[user_id] = {'websocket': websocket}  # 사용자 ID와 WebSocket 연결 저장
    await websocket.send_text(json.dumps({"type": "heartbeat"})) # 소켓연결 후 바로 하트비트 전결
    logger.debug(f"User connected: {user_id}")

    try:
        while True:
            message = await websocket.receive_text()
            # logger.debug(f"Received message from {user_id}: {message}")
            if "ping" in message:
                await websocket.send_text(json.dumps({"type": "heartbeat"})) 
                continue

            # 랜덤한 격언 선택
            quote_data = await get_random_quote()
            quote_content = quote_data[0]['q']  # 격언 내용
            quote_author = quote_data[0]['a']    # 격언 저자
            translated_quote = await translate_quote(quote_data[0])  # 격언 번역
            quote_message_data = {
                'id': 'server', # from
                'user_id': f'{user_id}', # to
                'msg': f"명언: {quote_content}\n번역: {translated_quote}\n\n- {quote_author} -",
                'read': True
            }
            # 서버에서 격언 메시지 전송
            mqtt_client.publish(mqtt_topic, json.dumps(quote_message_data))
            logger.debug(f'Sent quote: {quote_message_data}')
    except WebSocketDisconnect:
        logger.error(f"User disconnected: {user_id}")
        del clients[user_id]  # 사용자 ID로 연결 제거
    except Exception as e:
        logger.error(f"Error in websocket handling for user {user_id}: {e}")
        del clients[user_id]  # 오류 발생 시 연결 제거

app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4444)
