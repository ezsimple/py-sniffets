# %%
from keycloak import KeycloakOpenID
import os
from dotenv import load_dotenv

load_dotenv()
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET,
                                 realm_name=KEYCLOAK_REALM)

def login():
    username = 'yoon'
    password = '3134'
    try:
        token = keycloak_openid.token(username, password)
        print(token)
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    login()
