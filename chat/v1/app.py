import json
import uuid
import httpx
from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import paho.mqtt.client as mqtt
import asyncio
from kakaotrans import Translator
import time

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
PREFIX="/chat" 
router = APIRouter(prefix=PREFIX)

mqtt_broker = "127.0.0.1"
mqtt_topic = "chat/messages"
mqtt_client = mqtt.Client()

# WebSocket 연결 관리
clients = {}

# MQTT 메시지 수신 콜백
def on_message(client, userdata, message):
    message_data = json.loads(message.payload.decode())
    # 모든 WebSocket 클라이언트에 메시지 전송
    asyncio.run(send_message_to_clients(message_data))

mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker)
mqtt_client.subscribe(mqtt_topic)
mqtt_client.loop_start()  # MQTT 클라이언트 시작

async def send_message_to_clients(message_data):
    for client in clients.values():
        try:
            await client['websocket'].send_json(message_data)
        except Exception as e:
            print(f"Error sending message to client: {e}")

async def get_random_quote():
    '''
    격언 API
    '''
    async with httpx.AsyncClient() as client:
        response = await client.get("https://zenquotes.io/api/random")
        if response.status_code == 200:
            return response.json()
        return {"content": "격언을 가져오는 데 실패했습니다.", "author": "알 수 없음"}

async def translate_quote(quote):
    '''
    카카오 번역
    '''
    translator = Translator()
    loop = asyncio.get_event_loop()
    translated_text = await loop.run_in_executor(None, translator.translate, quote['q'], 'en', 'kr')
    return translated_text

@router.get("/")
async def get(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = str(uuid.uuid4())  # 사용자 ID 생성 (접속후 고정)
    await websocket.accept()

    clients[user_id] = {'websocket': websocket}  # 사용자 ID와 WebSocket 연결 저장
    print(f"User connected: {user_id}")

    try:
        while True:
            data = await websocket.receive_text()
            message_id = str(uuid.uuid4())
            message_data = {'id': message_id, 'user_id': user_id, 'msg': data, 'read': False}

            # 메시지를 MQTT에 전송
            mqtt_client.publish(mqtt_topic, json.dumps(message_data))
            print(f'Sent message: {message_data}')

            # 랜덤한 격언 선택
            quote_data = await get_random_quote()
            quote_content = quote_data[0]['q']
            quote_author = quote_data[0]['a']
            translated_quote = await translate_quote(quote_data[0])
            quote_message_data = {
                'id': user_id,
                'user_id': 'server',
                'msg': f"명언: {quote_content}\n번역: {translated_quote}\n\n- {quote_author} -",
                'read': True
            }
            # 서버에서 격언 메시지 전송
            mqtt_client.publish(mqtt_topic, json.dumps(quote_message_data))
            print(f'Sent quote: {quote_message_data}')
    except WebSocketDisconnect:
        print(f"User disconnected: {user_id}")
        del clients[user_id]  # 사용자 ID로 연결 제거
    except Exception as e:
        print(f"Error in websocket handling for user {user_id}: {e}")
        del clients[user_id]  # 오류 발생 시 연결 제거

app.include_router(router)  # 라우터 등록

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=4444)
