from __future__ import annotations
'''
.README 파일에서 # WARN "cron 표현식" 메시지 형식의 라인을 읽어와서 
현재 시간과 비교하여 일치하는 경우 메시지를 출력하는 유틸리티입니다.    
'''

import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


def get_readme_path() -> Path:
    try:
        return Path.home() / ".README"
    except Exception:
        return Path(".") / ".README"


README_PATH = get_readme_path()


def parse_warn_lines(file_path: Path) -> List[Tuple[str, str]]:
    pattern = re.compile(r'^# WARN "([^"]+)" (.+)$')

    results: List[Tuple[str, str]] = []

    try:
        if not file_path.exists():
            return results

        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")

                match = pattern.match(line)
                if match:
                    cron_expr, message = match.groups()
                    results.append((cron_expr.strip(), message.strip()))

    except Exception as e:
        print(f"[ERROR] 파일 읽기 실패: {e}")

    return results


def match_field(field: str, value: int, is_weekday: bool = False) -> bool:
    try:
        if field == "*":
            return True

        # 리스트
        if "," in field:
            return any(
                match_field(part.strip(), value, is_weekday)
                for part in field.split(",")
            )

        # step
        if field.startswith("*/"):
            step = int(field[2:])
            return value % step == 0

        # range
        if "-" in field:
            start, end = map(int, field.split("-"))

            if is_weekday:
                if start == 7:
                    start = 0
                if end == 7:
                    end = 0

            return start <= value <= end

        # 단일값
        num = int(field)

        if is_weekday and num == 7:
            num = 0

        return num == value

    except Exception:
        return False


def cron_match(expr: str, now: datetime) -> bool:
    try:
        minute, hour, day, month, weekday = expr.split()

        # Python → cron weekday 변환
        cron_weekday = (now.weekday() + 1) % 7

        return (
            match_field(minute, now.minute)
            and match_field(hour, now.hour)
            and match_field(day, now.day)
            and match_field(month, now.month)
            and match_field(weekday, cron_weekday, is_weekday=True)
        )
    except Exception:
        return False


def check_warnings() -> None:
    now = datetime.now()

    warn_list = parse_warn_lines(README_PATH)

    for cron_expr, message in warn_list:
        try:
            if cron_match(cron_expr, now):
                print(f"[WARN] {message}")
        except Exception as e:
            print(f"[ERROR] 처리 실패: {e}")


if __name__ == "__main__":
    check_warnings()
