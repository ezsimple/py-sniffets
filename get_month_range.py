#!/usr/bin/env python3
# encoding: utf-8

from datetime import date, datetime
from typing import Optional, Tuple
from range_factory import RangeFactory

def get_month_range(param: Optional[str] = None) -> Tuple[str, str]:
    """
    ES range용 한달 기간 계산

		허용 입력:
    - None
    - "YY-MM"
    - "YYYY-MM-dd"

    - param = None:
        지난달 01 ~ 이번달 01
    - param = "YY-MM" || param = "yyyy-MM-dd":
        전달 01 ~ 요청한 달 01
    - es의 gte, lt 의 파라미터
        gte start_date, lt end_date

    return: (start_date, end_date)  # yyyy-MM-dd
    """

    try:
        # 파라미터 없음 → 현재 월
        if param is None:
            today = date.today()
            base = date(today.year, today.month, 1)

        else:
            param = param.strip()

            # YYYY-MM-dd 우선 시도
            try:
                dt = datetime.strptime(param, "%Y-%m-%d")
                base = date(dt.year, dt.month, 1)

            except ValueError:
                # YY-MM 시도
                yy, mm = map(int, param.split("-"))
                base = date(2000 + yy, mm, 1)

    except Exception as e:
        raise ValueError(
            "param must be one of: None, 'YY-MM', 'YYYY-MM-dd'"
        ) from e

    # 전달 1일 계산
    if base.month == 1:
        prev_month = date(base.year - 1, 12, 1)
    else:
        prev_month = date(base.year, base.month - 1, 1)

    return (
        prev_month.strftime("%Y-%m-%d"),
        base.strftime("%Y-%m-%d"),
    )

import sys
if __name__ == '__main__':
	if len(sys.argv) > 1:
		param = sys.argv[1]
		start_date, end_date = get_month_range(param)
		print(f"{start_date} ~ {end_date}")
		sys.exit(0)

	start_date, end_date = get_month_range()
	print(f"{start_date} ~ {end_date}")
	
