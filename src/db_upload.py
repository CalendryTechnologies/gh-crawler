#! /usr/bin/env python

from sqlalchemy import Table, Column, String, create_engine, MetaData
import json

from os.path import join as pathjoin

from general import PROJECT_ROOT


DEBUG = True

def connect(url, db_args={}):
    con = create_engine(url, **db_args)
    meta = MetaData(bind=con, reflect=True)
    return con, meta

def mock_db(name):
    db_loc = pathjoin(PROJECT_ROOT, "mock_db", name + ".sqlite")
    url = "sqlite:///" + db_loc
    return connect(url)

CON, META = mock_db("test")

def make_events_table(events_dict, tablename="test"):
    columns = set()
    for event in events_dict["events"]:
        columns.update(event.keys())
    
    print(columns)

def mock_events(name):
    json_loc = pathjoin(PROJECT_ROOT, "mock_events", name + ".json")
    events = load_json(json_loc)
    return events

def load_json(filename):
    with open(filename, "r") as fp:
        return json.load(fp)

if __name__ == "__main__":
    con, meta = mock_db("test")
    events = mock_events("test")
    make_events_table(events, "test")
