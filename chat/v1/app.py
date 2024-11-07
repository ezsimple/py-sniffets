import json
import uuid
import httpx
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request, Cookie
import paho.mqtt.client as mqtt
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet
import time

'''
주의: crontab에서 크롤링중인 메소드를 사용중
테이블변경시 참고 필요
'''
from deep_translator import GoogleTranslator
from fastapi import APIRouter, HTTPException, Cookie, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from models.models import MinoLike, MinoQuote  # 모델 가져오기
from database import SessionLocal  # 데이터베이스 세션을 가져오는 방법
from logger import LoggerSetup
from crawling import add_quote
from pydantic import BaseModel

load_dotenv()
PREFIX = os.getenv("PREFIX","/chat")
WS_SERVER = os.getenv("WS_SERVER", f'ws://localhost:4444{PREFIX}/ws')
API_SERVER = os.getenv("API_SERVER1", 'https://zenquotes.io/api/random')
# Fernet key must be 32 url-safe base64-encoded bytes.
# SECRET_KEY = Fernet.generate_key().decode()  # 바이트를 문자열로 변환
SECRET_KEY = os.getenv("SECRET_KEY", "aEmolOFPK86VSPXrIkDHEQZRgjAjRXZuqt_N7Hi9wQ8=")
cipher = Fernet(SECRET_KEY)

# 로깅 설정
logger_setup = LoggerSetup()
logger = logger_setup.get_logger()

app = FastAPI()
app.mount("/chat/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix=PREFIX)
logger.info(f"WS_SERVER : {WS_SERVER}")

mqtt_broker = "127.0.0.1"
mqtt_client = mqtt.Client()

# WebSocket 연결 관리
clients = {}

# 마지막 요청 시간을 저장할 딕셔너리
last_request_time = {}

current_dir = os.path.dirname(os.path.abspath(__file__))

# 데이터베이스 세션을 생성하는 종속성
def get_db():
    db = SessionLocal()  # 새로운 데이터베이스 세션 생성
    try:
        yield db  # 요청에 대한 세션을 반환
    finally:
        db.close()  # 요청이 끝났을 때 세션을 닫음


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
        response = await client.get(API_SERVER)
        if response.status_code == 200:
            data = response.json()
            data[0]['quote_id'] = 0
            data[0]['like_count'] = 0
            if "zenquotes" in API_SERVER:
                if 'zenquotes.io' in data[0]['a']:
                    logger.warning(f'Warning: {data[0]}')
                    return data[0]
                quote = add_quote(data[0])
                if quote:
                    data[0]['quote_id'] = quote.id
                    data[0]['like_count'] = quote.like_count
            return data
        return {"content": "격언을 가져오는 데 실패했습니다.", "author": "알 수 없음"}

# async def translate_quote(quote):
#     translator = Translator()
#     loop = asyncio.get_event_loop()
#     translated_text = await loop.run_in_executor(None, translator.translate, quote['q'], 'en', 'kr')
#     return translated_text

async def translate_quote(quote):
    '''
    deep-L 라이브러리를 사용하여 번역하는 함수
    좀 더 자연어에 가까운 번역결과를 보여줌 
    '''
    translated_text = await asyncio.to_thread(GoogleTranslator(source='en', target='ko').translate, quote['q'])
    return translated_text  # 번역된 텍스트 반환

def get_readme_content(path):
    readme_path = os.path.join(path, '.README')
    if os.path.isfile(readme_path):
        with open(readme_path, 'r') as f:
            content = f.readlines()
        return '<br>'.join(line.strip() for line in content if not line.startswith('#'))
    return ""

@router.get("/")
async def get(request: Request, user_id: str = Cookie(None)):

    readme_content = get_readme_content(current_dir)
    timestamp = datetime.now().timestamp()  # 현재 시간을 타임스탬프로 변환
    response = templates.TemplateResponse("chat.html", {"request": request, "timestamp": timestamp, "WS_SERVER": WS_SERVER, "readme_content": readme_content})

    if user_id is None:
        user_id = str(uuid.uuid4())
        encrypted_user_id = cipher.encrypt(user_id.encode()).decode()
        response.set_cookie(key="user_id", value=encrypted_user_id, path='/')

    return response

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = Query(None)):
    '''
    WebSocket에서는 Cookie를 읽지 못하는 경우가 있음.
    그러므로 먼저 /에서 쿠키를 생성하고, 클라이언트에서 쿠키를 읽어서, 쿼리 파라미터로 전달하는 방식을 사용.
    '''
    # == start : websocket handshake
    if user_id is None:
        raise HTTPException(status_code=403, detail="User ID not provided")

    try:
        user_id = await decode_user_id(user_id)
    except Exception as e:
        await websocket.close(code=4000)
        raise e

    mqtt_topic = f"chat/messages/{user_id}"  # 사용자별 MQTT 토픽 생성
    mqtt_client.subscribe(mqtt_topic)  # 사용자별 MQTT 토픽 구독
    logger.debug(f"Subscribed to MQTT topic: {mqtt_topic}")
    # == end : websocket handshake

    await websocket.accept()
    clients[user_id] = {'websocket': websocket}  # 사용자 ID와 WebSocket 연결 저장
    last_request_time[user_id] = time.time()  # 초기화
    # await websocket.send_text(json.dumps({"type": "heartbeat"})) # 소켓연결 후 바로 하트비트 전결
    logger.debug(f"User connected: {user_id}")

    try:
        while True:
            message = await websocket.receive_text()
            if not isinstance(message, str):
                continue  # 문자열이 아닐 경우 다음 루프로 진행

            if "ping" in message:
                await websocket.send_text(json.dumps({"type": "heartbeat"})) 
                continue


            try:
                logger.debug(f"Received message from {user_id}: {message}")
                data = json.loads(message)
                max_row = data.get("MAX_ROW")
                li_count = int(data.get('liCount'))
                if li_count > max_row: # js 재연결 오류 발생시, 부하 방지
                    logger.warning(f"Too many messages: {li_count}")
                    continue

                current_time = time.time()
                if ((current_time - last_request_time[user_id] < 3) and (li_count >= max_row)):
                    logger.warning(f"Request from {user_id} ignored due to guard time.")
                    continue

                # 마지막 요청 시간 업데이트
                last_request_time[user_id] = current_time

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format: {message}")
                continue

            # 랜덤한 격언 선택
            quote_data = await get_random_quote()
            # 격언 데이터 가져오기
            quote_id = quote_data[0]['quote_id'] # 격언 ID
            quote_content = quote_data[0]['q']  # 격언 내용
            quote_author = quote_data[0]['a']    # 격언 저자
            quote_like_count = quote_data[0]['like_count'] # 좋아요 수
            translated_quote = await translate_quote(quote_data[0])  # 격언 번역
            quote_message_data = {
                'id': 'server', # from
                'user_id': f'{user_id}', # to
                'quote_id': f'{quote_id}',
                'msg': f"명언: {quote_content}\n번역: {translated_quote}\n\n- {quote_author} -",
                'like_count': f'{quote_like_count}',
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
        del clients[user_id] 

async def decode_user_id(user_id):
    try:
        user_id = cipher.decrypt(user_id.encode()).decode()  # 복호화
        return user_id
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        # 쿠키 제거
        response = HTMLResponse()
        response.set_cookie(key="user_id", value="", expires=0)  # 쿠키 제거
        raise HTTPException(status_code=400, detail="Invalid user ID")

class LikeQuoteRequest(BaseModel):
    quote_id: int

from pydantic import BaseModel

class LikeQuoteRequest(BaseModel):
    quote_id: int

@router.post("/like")
async def like_quote(request: LikeQuoteRequest, user_id: str = Cookie(None), db: Session = Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=403, detail="User ID not provided")

    user_id = await decode_user_id(user_id)
    quote_id = request.quote_id  # Pydantic 모델에서 quote_id 가져오기
    like_record = db.query(MinoLike).filter(MinoLike.user_id == user_id, MinoLike.quote_id == quote_id).first()

    if like_record:
        # 이미 좋아요를 눌렀다면 현재 좋아요 수를 반환
        quote = db.query(MinoQuote).filter(MinoQuote.id == quote_id).first()
        return {"message": "Quote already liked", "like_count": quote.like_count}

    # 좋아요 기록 추가
    new_like = MinoLike(user_id=user_id, quote_id=quote_id)
    db.add(new_like)  # 세션에 새로운 좋아요 추가
    db.commit()  # 변경 사항 커밋

    # 좋아요 수 증가
    quote = db.query(MinoQuote).filter(MinoQuote.id == quote_id).first()
    if quote:
        quote.like_count += 1  # 좋아요 수 증가
        db.commit()  # 변경 사항 커밋

    return {"message": "Quote liked successfully", "like_count": quote.like_count}


app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4444)
