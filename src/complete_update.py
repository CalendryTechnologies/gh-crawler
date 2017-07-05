'''
Combines the various parts of the calendar update process to produce a csv file for upload on request.
'''

from os.path import join as pathjoin, isdir
from os import listdir, walk as walkdir
import json
import csv

from structured_parser import extract_from_template
from db_upload import get_newevents, pull_events
from event_cmp import EventList, printEL
from json2csv import json2csv
from general import ASSETS_DIR, DEBUG, nowstr, move_dir, mkdir


TEMPLATE = "hartsvillesc.json" # template filename in ASSETS_DIR/templates directory
COMPARISON_KWARGS = {} # **kwargs for passing to EL.by_matching for comparison

def full_update():
    
    ## Use template to extract from multiple sites
    template = pathjoin(ASSETS_DIR, "templates", TEMPLATE)
    extract_from_template(template, debug=DEBUG)
    
    ## Gather all new events from the extraction and put them into a single EventList
    newevents_dir = pathjoin(ASSETS_DIR, "newevents")
    files = sorted(listdir(newevents_dir)) #directories sorted by date created oldest to newest
    new_events = EventList([]) #list of new events lists from oldest to newest
    for directory in files:
        dir_path = pathjoin(newevents_dir, directory)
        if isdir(dir_path) and directory.isnumeric():
            for root, dirs, files in walkdir(dir_path):
                #TODO handle case when outputdir is different
                for file in files:
                    asset_path = pathjoin(root, file)
                    with open(asset_path, "r") as fp:
                        newEL = EventList(json.load(fp)['events'])
                    # if DEBUG: printEL(newEL)
                    new_events = newEL.union(new_events) #update newevents to contain the new items in most recent form
    
    ## Compare with events already on GoHartsville.com and convert to csv
    current_events = pull_events() #pull events from GoHartsville REST API
    upload_events = new_events.intersection(current_events) #find difference between lists so only new events are uploaded
    csv_upload_events = json2csv(upload_events, csv_headers=None, remapping={})
    
    ## Clean up results directory
    results_dir = pathjoin(ASSETS_DIR, "results")
    results_cache = pathjoin(ASSETS_DIR, "cache", "results")
    mkdir(results_cache)
    move_dir(results_dir, results_cache)
        
    ## Write csv to results
    results_path = pathjoin(results_dir, nowstr() + ".csv")
    with open(results_path, "w+") as fp:
        writer = csv.writer(fp)
        writer.writerows(csv_upload_events)
    
    ## Clean up newevents directory
    newevents_cache = pathjoin(ASSETS_DIR, "cache", "newevents")
    mkdir(newevents_cache)
    move_dir(newevents_dir, newevents_cache)

def main():
    full_update()
    
if __name__ == "__main__":
    main()
    