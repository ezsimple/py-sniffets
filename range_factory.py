#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from datetime import date, datetime, time, timedelta
from typing import Optional, Tuple
from enum import Enum
from zoneinfo import ZoneInfo


# =========================
# Timezone Enum
# =========================
class TZ(Enum):
    KST = "Asia/Seoul"
    UTC = "UTC"

    @property
    def zoneinfo(self) -> ZoneInfo:
        return ZoneInfo(self.value)


# =========================
# RangeFactory
# =========================
class RangeFactory:
    """
    날짜 범위 계산 Factory

    기본 정책
    - 계산 기준 TZ: KST
    - 기본 출력 포맷: yyyy-MM-dd
    - default 는 '사람 기준 날짜'
    - ES 용일 때만 as_utc=True + iso=True 사용
    """

    DEFAULT_FMT = "%Y-%m-%d"

    # ---------- internal ----------
    @staticmethod
    def _format(dt: datetime, *, iso: bool, fmt: str) -> str:
        if iso:
            return dt.isoformat()
        return dt.strftime(fmt)

    # =========================
    # Month Range
    # =========================
    @staticmethod
    def month(
        param: Optional[str] = None,
        tz: TZ = TZ.KST,
        *,
        fmt: str = DEFAULT_FMT,
        iso: bool = False,
        as_utc: bool = False,
    ) -> Tuple[str, str]:
        """
        지난달 1일 ~ 기준월 1일

        param:
          - None
          - 'YY-MM'
          - 'YYYY-MM-dd'
        """

        tzinfo = tz.zoneinfo

        try:
            # 기준 월 결정
            if param is None:
                now = datetime.now(tzinfo)
                base = date(now.year, now.month, 1)

            elif len(param) == 5:  # YY-MM
                yy, mm = map(int, param.split("-"))
                base = date(2000 + yy, mm, 1)

            else:  # YYYY-MM-dd
                dt = datetime.strptime(param, "%Y-%m-%d")
                base = date(dt.year, dt.month, 1)

        except Exception as e:
            raise ValueError(
                "param must be None, 'YY-MM', or 'YYYY-MM-dd'"
            ) from e

        # 이전 달 1일
        if base.month == 1:
            prev = date(base.year - 1, 12, 1)
        else:
            prev = date(base.year, base.month - 1, 1)

        # KST 기준 00:00
        gte = datetime.combine(prev, time.min, tzinfo)
        lt = datetime.combine(base, time.min, tzinfo)

        # ES 용일 때만 UTC 변환
        if as_utc:
            gte = gte.astimezone(ZoneInfo("UTC"))
            lt = lt.astimezone(ZoneInfo("UTC"))

        return (
            RangeFactory._format(gte, iso=iso, fmt=fmt),
            RangeFactory._format(lt, iso=iso, fmt=fmt),
        )

    # =========================
    # Week Range
    # =========================
    @staticmethod
    def week(
        param: Optional[str] = None,
        tz: TZ = TZ.KST,
        *,
        fmt: str = DEFAULT_FMT,
        iso: bool = False,
        as_utc: bool = False,
    ) -> Tuple[str, str]:
        """
        지난주 월요일 ~ 이번주 월요일

        param:
          - None
          - 'YYYY-MM-dd'
        """

        tzinfo = tz.zoneinfo

        try:
            if param is None:
                base = datetime.now(tzinfo).date()
            else:
                base = datetime.strptime(param, "%Y-%m-%d").date()

        except ValueError as e:
            raise ValueError(
                "param must be None or 'YYYY-MM-dd'"
            ) from e

        # 이번주 월요일
        this_monday = base - timedelta(days=base.weekday())
        last_monday = this_monday - timedelta(days=7)

        gte = datetime.combine(last_monday, time.min, tzinfo)
        lt = datetime.combine(this_monday, time.min, tzinfo)

        if as_utc:
            gte = gte.astimezone(ZoneInfo("UTC"))
            lt = lt.astimezone(ZoneInfo("UTC"))

        return (
            RangeFactory._format(gte, iso=iso, fmt=fmt),
            RangeFactory._format(lt, iso=iso, fmt=fmt),
        )
