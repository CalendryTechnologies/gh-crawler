from dotenv import load_dotenv, find_dotenv
from sqlalchemy import Table, Column, String, create_engine, MetaData

import os

def connect(url):
    con = create_engine(url, client_encoding='utf8')
    meta = MetaData(bind=con, reflect=True)
    return con, meta

if __name__ == "__main__":
    load_dotenv(find_dotenv())
    url = os.environ.get("DATABASE_URL")

    con, meta = connect(url)
