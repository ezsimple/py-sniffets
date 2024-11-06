# %%
import nest_asyncio
import asyncio
from googletrans import Translator

nest_asyncio.apply()

async def translate_quote(quote):
    translator = Translator()
    loop = asyncio.get_event_loop()
    
    # 비동기적으로 번역 수행
    translated_text = await loop.run_in_executor(None, translator.translate, quote['q'], 'en', 'ko')
    return translated_text.text  # 번역된 텍스트 반환

# 예제 사용
async def main():
    quote = {'q': "It's raining cats and dogs."}
    translated = await translate_quote(quote)
    print(translated)

# 실행
if __name__ == "__main__":
    asyncio.run(main())