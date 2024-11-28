#!/bin/bash
# KEYCLOAK=https://a1.mkeasy.kro.kr/auth
# curl -X POST "$KEYCLOAK/realms/MinoRealm/protocol/openid-connect/token" \
# -H "Content-Type: application/x-www-form-urlencoded" \
# -d "client_id=file-download-app" \
# -d "client_secret=leiXXLa6GawOYzAH2aPRVwc4GM6J2Ncx" \
# -d "username=yoon" \
# -d "password=3134" \
# -d "grant_type=password"

# .env 파일에서 환경 변수 로드
set -a # 모든 변수를 자동으로 export
source .env
set +a  # 자동 export 해제

# 인증 요청
curl -X POST "$KEYCLOAK_SERVER_URL/realms/$KEYCLOAK_REALM/protocol/openid-connect/token" \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "client_id=$KEYCLOAK_CLIENT_ID" \
-d "client_secret=$KEYCLOAK_CLIENT_SECRET" \
-d "username=$USERNAME" \
-d "password=$PASSWORD" \
-d "grant_type=password"
