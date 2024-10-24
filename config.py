from dotenv import load_dotenv
import os

load_dotenv()




DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOSTNAME = os.environ.get('DB_HOSTNAME')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')
TOKEN_SECRET = os.environ.get('TOKEN_SECRET')
USER_MANAGER_SECRET = os.environ.get('USER_MANAGER_SECRET')