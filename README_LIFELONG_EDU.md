# 평생교육이용권 공지 모니터링 프로그램

평생교육이용권 신청/접수 공지사항을 자동으로 모니터링하고 새로운 공지가 나오면 텔레그램으로 알림을 보내는 프로그램입니다.

## 기능

- 🕐 **자동 모니터링**: crontab을 통해 정기적으로 실행
- 🔍 **웹 스크래핑**: Playwright를 사용한 안정적인 웹 페이지 접근
- 📊 **목록수 비교**: 이전 목록수와 현재 목록수를 비교하여 변경 감지
- 📱 **텔레그램 알림**: 새로운 공지 발견 시 상세한 알림 메시지 발송
- 📝 **로그 기록**: 모든 활동을 로그 파일에 기록
- ⚙️ **설정 관리**: JSON 파일을 통한 설정 저장 및 로드

## 설치

### 1. 필요한 패키지 설치

```bash
pip install playwright python-dotenv requests
playwright install chromium
```

### 2. 환경변수 설정

`env.example` 파일을 복사하여 `.env` 파일을 생성하고 실제 값으로 변경하세요:

```bash
cp env.example .env
```

`.env` 파일에서 다음 값들을 설정하세요:

```env
# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 3. 텔레그램 봇 설정

1. **봇 생성**: 텔레그램에서 @BotFather를 찾아 `/newbot` 명령으로 새 봇 생성
2. **토큰 확인**: BotFather가 제공하는 봇 토큰을 `TELEGRAM_BOT_TOKEN`에 설정
3. **채팅 ID 확인**: 
   - 봇과 대화를 시작
   - 브라우저에서 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` 접속
   - `chat_id` 값을 `TELEGRAM_CHAT_ID`에 설정

## 사용법

### 수동 실행

```bash
# 기본 실행
python lifelong_edu.py

# 로그 확인
tail -f lifelong_edu.log
```

### 자동 실행 (crontab)

```bash
# crontab 편집
crontab -e

# 다음 라인 추가 (매일 오전 9시 실행)
0 9 * * * cd /path/to/your/project && /usr/bin/python3 lifelong_edu.py >> /path/to/your/project/cron.log 2>&1
```

### 텔레그램 봇 테스트

```bash
python TelegramSimpleBot.py
```

## 설정

### 지역별 설정

`lifelong_edu.py` 파일의 `LifelongEducationMonitor` 클래스에서 지역별 설정을 수정할 수 있습니다:

```python
self.regions = {
    'chungnam': {
        'name': '충청남도',
        'url': 'https://www.lllcard.kr/reg/chungnam/cop/bbs/selectBoardList.do',
        'current_count': 9,
        'search_keyword': '평생교육'
    },
    'gyeonggi': {
        'name': '경기도',
        'url': '',  # URL 추가 필요
        'current_count': 0,
        'search_keyword': '평생교육'
    }
}
```

### 설정 파일

프로그램 실행 후 `lifelong_edu_config.json` 파일이 생성되어 현재 목록수가 저장됩니다:

```json
{
  "chungnam": {
    "current_count": 9,
    "last_updated": "2024-01-01T09:00:00"
  }
}
```

## 로그

- **로그 파일**: `lifelong_edu.log`
- **cron 로그**: `cron.log` (crontab 설정 시)

로그 예시:
```
2024-01-01 09:00:00 - INFO - 평생교육이용권 공지 모니터링 시작
2024-01-01 09:00:01 - INFO - 충청남도 모니터링 시작
2024-01-01 09:00:05 - INFO - 충청남도 공지사항 페이지 접속 중...
2024-01-01 09:00:08 - INFO - 충청남도 검색어 입력: 평생교육
2024-01-01 09:00:10 - INFO - 충청남도 검색 결과: 9건
2024-01-01 09:00:10 - INFO - 충청남도 - 이전: 9건, 현재: 9건
2024-01-01 09:00:10 - INFO - 충청남도 새로운 공지 없음
```

## 알림 메시지 예시

새로운 공지가 발견되면 다음과 같은 텔레그램 메시지가 발송됩니다:

```
🔔 평생교육이용권 새로운 공지가 나왔습니다!

📍 지역: 충청남도
📊 이전 목록수: 9건
📊 현재 목록수: 12건
📈 증가: 3건
⏰ 확인시간: 2024-01-01 09:00:10
```

## 문제 해결

### 웹페이지 접근 오류
- 네트워크 연결 확인
- 웹사이트 구조 변경 여부 확인
- Playwright 브라우저 업데이트: `playwright install chromium`

### 텔레그램 알림 오류
- 봇 토큰과 채팅 ID 확인
- 봇과의 대화 시작 여부 확인
- 네트워크 연결 확인

### crontab 실행 오류
- 절대 경로 사용 확인
- Python 경로 확인: `which python3`
- 로그 파일 권한 확인

## 파일 구조

```
├── lifelong_edu.py              # 메인 모니터링 프로그램
├── TelegramSimpleBot.py         # 텔레그램 봇 클래스
├── lifelong_edu_config.json     # 설정 파일 (자동 생성)
├── lifelong_edu.log             # 로그 파일 (자동 생성)
├── .env                         # 환경변수 파일 (직접 생성)
├── env.example                  # 환경변수 예시 파일
├── crontab_example.txt          # crontab 설정 예시
└── README_LIFELONG_EDU.md       # 이 파일
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 