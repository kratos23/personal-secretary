#!.venv/bin/python
import sqlite3
import dotenv
from sqlalchemy import Boolean, Column, Integer, String, Table, MetaData, create_engine

db_name = dotenv.get_key(dotenv.find_dotenv(), "db_name")

conn = sqlite3.connect(db_name)
conn.close()

enigne = create_engine(f"sqlite:///{db_name}", echo=True)
meta = MetaData()

user_table = Table(
    "user",
    meta,
    Column("id", Integer, primary_key=True),
    Column("credentials", String, nullable=True),
    Column("is_finished", Boolean, default=False),
)

meta.create_all(enigne)
