import requests

KEYCLOAK_SERVER_URL = 'https://a1.mkeasy.kro.kr/auth'
KEYCLOAK_REALM = 'MinoRealm'
KEYCLOAK_CLIENT_ID = 'file-download-app'
KEYCLOAK_CLIENT_SECRET = 'leiXXLa6GawOYzAH2aPRVwc4GM6J2Ncx'

def login():
    username = 'yoon'
    password = '3134'
    url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    
    data = {
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
        'username': username,
        'password': password,
        'grant_type': 'password'
    }
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print("토큰:", response.json())
    else:
        print("오류:", response.status_code, response.text)

if __name__ == "__main__":
    login()
