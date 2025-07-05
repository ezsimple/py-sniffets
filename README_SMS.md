# SMS 발송 프로그램

SOLAPI를 사용하여 SMS를 발송하는 Python 프로그램입니다.

## 설치

### 1. 필요한 패키지 설치

```bash
pip install python-dotenv solapi
```

### 2. 환경변수 설정

`env.example` 파일을 복사하여 `.env` 파일을 생성하고 실제 값으로 변경하세요:

```bash
cp env.example .env
```

`.env` 파일에서 다음 값들을 설정하세요:

```env
# SOLAPI API 키 (SOLAPI 대시보드에서 확인)
SOL_API_KEY=your_api_key_here

# SOLAPI API Secret (SOLAPI 대시보드에서 확인)
SOL_API_SECRET=your_api_secret_here

# 발신번호 (등록된 발신번호만 사용 가능, 010으로 시작하는 11자리 숫자)
SOL_HP=01012345678
```

## 사용법

### 기본 사용법

```bash
python sms.py <수신번호> <메시지>
```

### 예시

```bash
# 단순한 메시지 발송
python sms.py 01012345678 "안녕하세요! SMS 테스트입니다."

# 긴 메시지 발송 (따옴표로 감싸기)
python sms.py 01012345678 "안녕하세요! 이것은 긴 메시지입니다. 여러 줄로 작성할 수 있습니다."
```

## 주의사항

1. **수신번호 형식**: 010으로 시작하는 11자리 숫자여야 합니다.
2. **발신번호**: SOLAPI에 등록된 발신번호만 사용 가능합니다.
3. **API 키**: SOLAPI 대시보드에서 발급받은 API 키와 Secret을 사용하세요.
4. **메시지 길이**: SMS는 일반적으로 90바이트(한글 45자)를 초과하면 여러 건으로 분할 발송됩니다.

## 오류 해결

### 환경변수 오류
- `.env` 파일이 프로젝트 루트 디렉토리에 있는지 확인
- 환경변수 이름이 정확한지 확인 (SOL_API_KEY, SOL_API_SECRET, SOL_HP)

### 번호 형식 오류
- 수신번호와 발신번호 모두 010으로 시작하는 11자리 숫자여야 함
- 하이픈(-)이나 공백 없이 숫자만 입력

### API 오류
- SOLAPI 대시보드에서 API 키와 Secret이 올바른지 확인
- 발신번호가 SOLAPI에 등록되어 있는지 확인
- 계정 잔액이 충분한지 확인

## 파일 구조

```
├── sms.py              # SMS 발송 메인 프로그램
├── .env                # 환경변수 파일 (직접 생성)
├── env.example         # 환경변수 예시 파일
└── README_SMS.md       # 이 파일
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 