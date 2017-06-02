#! /usr/bin/env python

'''
Diffs new findings and uploaded files (via wp REST API) then outputs json file with only new events 
'''

import json
from datetime import datetime
from os.path import join as pathjoin
import requests

from general import PROJECT_ROOT


DEBUG = True
ASSETS_DIR = pathjoin(PROJECT_ROOT, "mock")
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
    return EventDict(get_json_asset("events", name)["events"])

def get_newevents(name):
    return EventDict(get_json_asset("newevents", name)["events"])

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

class EventDict(list):
    def by_datetime(self, start, stop=None):
        if stop is None:
            def same_date(event):
                start_str = event.get("start_date")
                if not start_str:
                    return False
                else:
                    return datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S") == start
                
            return EventDict(filter(same_date, self))
        
        else:
            def in_range(event):
                start_str = event.get("start_date")
                if not start_str:
                    return False
                else:
                    start_datetime = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    return start <= start_datetime <= stop
            
            return EventDict(filter(in_range, self))

def printE(events):
    ret = "[\n"
    for ev in events:
        ret += "  %s (%s to %s)\n" % (
            ev.get("title"), 
            ev.get("start_date") or ev.get("start"),
            ev.get("end_date") or ev.get("stop")
        )
    ret += "]"
    print(ret)

if __name__ == "__main__":
    #printE(pull_events())
    events = get_events("test")
    printE(events)
    new_events = get_newevents("test")
    printE(new_events)
    start = datetime.strptime("2007-04-12 19:00:00", "%Y-%m-%d %H:%M:%S")
    stop = datetime.strptime("2007-05-13 19:00:00", "%Y-%m-%d %H:%M:%S")
    printE(events.by_datetime(start, stop))
