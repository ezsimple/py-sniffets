# %%
from create_tables import session
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import sys

def truncate_tables():
    '''
    truncate 직후 대량의 insert 작업은 db을 블로킹 모드로 보낼 수 있음.
    '''
    try:
        session.execute(text(f'TRUNCATE TABLE public."MinoWeatherHourly";'))
        session.execute(text(f'TRUNCATE TABLE public."MinoWeatherDaily";'))
        session.execute(text(f'TRUNCATE TABLE public."MinoWeatherWeekly";'))
        session.execute(text(f'TRUNCATE TABLE public."MinoWeatherMonthly";'))
    except SQLAlchemyError as e:
        session.rollback()  # 트랜잭션 롤백
        print(f"Error inserting data: {e}")
        sys.exit(-1)

    # 변경사항 커밋
    session.commit()

if __name__ == "__main__":
    truncate_tables()
