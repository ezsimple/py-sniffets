import os
import sys
from groq import Groq
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("GRQ_API_KEY")
client = Groq(api_key=api_key)

# 모델 목록 조회
models_response = client.models.list()

# 모델 데이터 접근 (data 속성에 모델 리스트가 있음)
models = models_response.data if hasattr(models_response, 'data') else []
print(f"Found {len(models)} models")

# llama가 포함된 모델 검색
# print("\nModels containing 'llama' in their ID:")
# print("-" * 50)
# llama_models = [m for m in models if hasattr(m, 'id') and 'llama' in m.id.lower()]

# for model in llama_models:
#     print(f"ID: {model.id}")
#     print(f"Created: {model.created}")
#     print(f"Owned by: {model.owned_by}")
#     print(f"Context window: {model.context_window} tokens")
#     print("-" * 50)

argv = ''.join(sys.argv[1:])
if argv == "":
    print("Usage: python groq_hello.py <message>")
    sys.exit(1)

MODEL="llama-3.3-70b-versatile"
chat_completion = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": argv}
    ]
)
print(chat_completion.choices[0].message.content)