import asyncio
from kakaotrans import Translator

async def translate_quote(quote):
    translator = Translator()
    loop = asyncio.get_event_loop()
    
    # 비동기적으로 번역 수행
    translated_text = await loop.run_in_executor(None, translator.translate, quote['q'], 'en', 'kr')
    return translated_text

# 예제 사용
async def main():
    quote = {'q': "It's raining cats and dogs."}
    translated = await translate_quote(quote)
    print(translated)

# 실행
if __name__ == "__main__":
    asyncio.run(main())