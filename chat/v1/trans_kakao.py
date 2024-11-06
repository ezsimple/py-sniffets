# %%
import nest_asyncio
import asyncio
from kakaotrans import Translator

'''
Jupyter Notebook에서 asyncio를 사용할 때 발생하는 오류는 
종종 이벤트 루프와 관련된 문제로 인해 발생합니다. 
Jupyter Notebook은 이미 자체 이벤트 루프를 실행하고 있기 때문에, 
이를 적절하게 관리해야 합니다. 

nest_asyncio는 주로 Jupyter Notebook과 같은 환경에서 필요합니다. 
일반적인 Python 스크립트나 다른 IDE(예: PyCharm, VSCode)에서는 
asyncio를 사용하는 데 nest_asyncio가 필요하지 않습니다. 
그 이유는 이러한 환경에서는 기본 이벤트 루프를 직접 사용할 수 있기 때문입니다.
'''
# nest_asyncio 적용
nest_asyncio.apply()

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