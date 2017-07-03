#! /usr/bin/env python

'''
Diffs new findings and uploaded files (via wp REST API) then outputs json file with only new events 
'''

import json
from os.path import join as pathjoin
import requests

from general import DEBUG, ASSETS_DIR
from event_cmp import EventList, printEL
from json2csv import json2csv


GH_API_URL = "http://gohartsville.com/wp-json/tribe/events/v1/events?per_page=50&page={page}"
EMPTY_CODE = "event-archive-page-not-found"

def get_json_asset(asset_type, name):
    json_loc = pathjoin(ASSETS_DIR, asset_type, name + ".json")
    events = load_json(json_loc)
    return events

def dump_json_asset(asset_type, name, obj):
    json_loc = pathjoin(ASSETS_DIR, asset_type, name + ".json")
    with open(json_loc, "w+") as fp:
        json.dump(obj, fp, indent=2)
    
def get_events(name):
    return EventList(get_json_asset("events", name)["events"])

def get_newevents(name):
    return EventList(get_json_asset("newevents", name)["events"])

def load_json(filename):
    with open(filename, "r") as fp:
        return json.load(fp)

def pull_events(save_to=None):
    '''
    Pulls events from the GoHartsville site
    :param save_to: if not None, json file is saved to this location in events directory
    '''
    i = 1
    url = GH_API_URL.replace("{page}", str(i))
    page = requests.get(url).json()
    #if DEBUG: print("> pull_events: pulled %s" % url)
    events = page.get("events")
    done = False
    
    while not done:
        i += 1
        url = GH_API_URL.replace("{page}", str(i))
        page = requests.get(url).json()

        #if DEBUG: print("> pull_events: pulled %s" % url)
        
        if page.get("code") == EMPTY_CODE:
            done = True
        else:
            events.extend(page.get("events"))
    
    #if DEBUG: print("> pull_events: event count = %d" % len(events))
    
    if save_to is not None:
        dump_json_asset("events", save_to, {"events":events})
    
    return events

def main():
    #printEL(pull_events())
    events = get_events("test")
    printEL(events)
    new_events = get_newevents("test")
    printEL(new_events)
    start = "2017-03-29 19:00:00"
    stop = "2017-04-15 19:00:00"
    printEL(events.by_datetime(start, stop, form="text").by_matching(events[2], threshold=0.9))
    
    with open(pathjoin(ASSETS_DIR, "tests", "test.csv"), "w+") as fp:
        import csv
        writer = csv.writer(fp)
        writer.writerows(json2csv(new_events, csv_headers=None))

if __name__ == "__main__":
    main()
