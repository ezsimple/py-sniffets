# %%
from deep_translator import GoogleTranslator
import nest_asyncio
import asyncio

# nest_asyncio 적용
nest_asyncio.apply()

async def translate_quote(quote):
    # 비동기적으로 번역 수행
    translated_text = await asyncio.to_thread(GoogleTranslator(source='en', target='ko').translate, quote['q'])
    return translated_text  # 번역된 텍스트 반환

# 예제 사용
async def main():
    quote = {'q': "It's raining cats and dogs."}
    translated = await translate_quote(quote)
    print(translated)

# 실행
if __name__ == "__main__":
    asyncio.run(main())