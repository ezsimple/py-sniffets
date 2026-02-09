#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from datetime import date, datetime, timedelta
from typing import Optional, Tuple
from range_factory import RangeFactory

def get_week_range(param: Optional[str] = None) -> Tuple[str, str]:
    """
    ES range용 주간 기간 계산

    기준:
    - 지난주 월요일 ~ 이번주 월요일 (gte, lt)

    허용 파라미터:
    - None
    - "YYYY-MM-dd"
    """

    try:
        # 1. 기준 날짜 결정
        if param is None:
            base_date = date.today()
        else:
            base_date = datetime.strptime(param.strip(), "%Y-%m-%d").date()

    except ValueError as e:
        raise ValueError(
            "param must be None or 'YYYY-MM-dd'"
        ) from e

    # 2. 이번주 월요일
    # weekday(): 월=0, 화=1, ..., 일=6
    this_monday = base_date - timedelta(days=base_date.weekday())

    # 3. 지난주 월요일
    last_monday = this_monday - timedelta(days=7)

    # 4. ES friendly format
    return (
        last_monday.strftime("%Y-%m-%d"),
        this_monday.strftime("%Y-%m-%d"),
    )

import sys
if __name__ == '__main__':
	if len(sys.argv) > 1:
		param = sys.argv[1]
		start_date, end_date = get_week_range(param)
		print(f"{start_date} ~ {end_date}")
		sys.exit(0)

	start_date, end_date = get_week_range()
	print(f"{start_date} ~ {end_date}")
	
