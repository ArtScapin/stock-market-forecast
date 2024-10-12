import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

def openDatabaseConnection():
    load_dotenv()
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    name = os.getenv('DB_NAME')

    connString = f'postgresql://{user}:{password}@{host}:{port}/{name}'
    engine = create_engine(connString)

    return engine