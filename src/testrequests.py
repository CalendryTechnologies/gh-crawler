#! /usr/bin/env python

#TODO Current Issues:
# * If a time is not specified for the second date (as in prom setup) the stop datetime is not recorded
# * The date is not carried over from the start time so the stop time defaults to today if there is none provided
# * It may be better to explore the single page about the event which has more details
#  * More steps to get to the item means more could go wrong
#  * More requesting time since each event will be it's own request on top of the ones already requested for lists

from lxml import html
import requests
import json
import string
import itertools

from datetime import datetime
import dateutil.parser as dateutil #TODO actually use this

import os, sys
from os.path import join as pathjoin, abspath, dirname


def project_root():
    '''
    Gets absolute path of project root

    :return: Returns absolute path string for project root directory
    '''
    return pathjoin(dirname(abspath(sys.argv[0])), "..") #gets root of

def extract_from_template(json_filename):
    '''
    Reads json template file then extracts data according to its rules and writes it where specified
    '''
    template = get_template(pathjoin(project_root(), "templates", json_filename)) #filename in templates directory
    extract(template)

def get_template(json_filename):
    '''
    Reads from a file and gets the json template object
    '''
    with open(json_filename) as fp:
        return json.load(fp)

def partition_rules(rules_dict):
    '''
    Get annotations (modifiers) and processes (things to process) from rules_dict

    :param rules_dict: Dictionary with keys starting with @ (annotations) and letters (processes)
    :return: Returns lists of (annotations, processes)
    '''
    others = {k:v for k,v in rules_dict.items() if len(k) > 0}
    annotations = {k:v for k,v in others.items() if len(k) > 0 and k[0] == "@"}
    processes = {k:v for k,v in others.items() if len(k) > 0 and k[0] in string.ascii_letters}

    return annotations, processes

def extract(rules_dict):
    '''
    Extracts an entire set of data based on a rules dictionary
    '''
    annotations, processes = partition_rules(rules_dict)

    output_dir = pathjoin(project_root(), (annotations.get("@output_dir") or ".")) #get output_dir or use blank relative path #TODO possibly need to use . for relative location

    for process_key in processes:
        #loop through each process and complete it
        #TODO do this with threading/multiprocessing since they are all separate
        process_rules = rules_dict[process_key]
        process_output = pathjoin(output_dir, process_key + ".json") #save to process_key with .json extension
        extract_process(process_rules, process_output) #extract from the individual process

def get_variables(annotations):
    '''
    Gets all variables over which the process iterates (start with @var and @list)

    :param annotations: Dictionary with all keys beginning with @
    :return: Returns two dictionaries (one with vars and one with lists mapped by name)
    '''
    variables = {}
    lists = {}

    for annotation in annotations.items():
        if annotation[0].startswith("@var:"):
            variables[annotation[0].replace("@var:", "")] = annotation[1]
        if annotation[0].startswith("@list:"):
            lists[annotation[0].replace("@list:", "")] = annotation[1]

    return variables, lists

def extract_process(rules_dict, output_file, variables={}):
    annotations, misc = partition_rules(rules_dict) #get annotations and misc (there shouldn't be anything without annotation)

    new_variables, new_lists = get_variables(annotations)
    variables.update(new_variables) #add variables to the dictionary
    variables.update({k:v[0] for k,v in new_lists.items() if len(v) > 0}) #put first value of each list in dictionary

    url = annotations.get("@url")
    if url == None: return False #url is required for process

    done = False
    while not done:
        for var in variables.items():
            url = url.replace("{$%s}" % var[0], str(var[1])) #replace any instance of variables in url
            extract_nodes_from_url(url, rules_dict, output_file)

        done = True #TODO add done condition of all variables exhausted or there are no variables

    return True

def extract_nodes_from_url(url, rules_dict, output_file, variables={}):
    '''
    Extracts a complete node from a document via ruled dictionary from url (allows use of threading)

    :param url: String url to pull from
    :rules_dict: dictionary with node rules
    :param output_file: filename to write to (absolute)
    :param variables: dictionary of variables to use
    :return: Returns success rate boolean
    '''
    print(url) #TODO remove
    pass #TODO

def extract_nodes(doc_root, rules_dict, output_file, variables={}):
    '''
    Extracts a complete node from a document via a ruled dictionary

    :param doc_root: document root element (created by lxml.html.fromstring())
    :rules_dict: dictionary with node rules
    :param output_file: filename to write to (absolute)
    :param variables: dictionary of variables to use
    :return: Returns success rate boolean
    '''
    pass

def inner_extract(doc_root, node_root, node_details, output_file, variables={}):
    '''
    Extracts data from a site according to rules

    :param doc_root: document root element (created by lxml.html.fromstring())
    :param node_root: string xpath for node root (all other nodes will be relative to root)
    :param node_details: dictionary of string item names to their string xpath locations
    :param output_file: filename to put results in
    :param variables: dictionary of string variable names to their values
    :return: Returns a json-like python object if no output file is specified else None
    '''

    pass #TODO read xpaths from dictionary and get data

if __name__ == "__main__":
    pg_num = 1
    done = False #have we finished looping through pages
    datetime_parse_fmt = "%B %-d @ %I:%M %p" #format string for getting datetime object
    datetime_fmt = "%m/%d/%Y %H:%M:%S" #format datetime should be in for standardization
    event_list = [] #list of events to be put together (each event will be dictionary)

    #TODO TODO TODO remove this debugging part
    while not done and pg_num < 3 and False:
        #Loop through all pages of the calendar

        page = requests.get('https://www.hartsvillesc.gov/calendar/?action=tribe_photo&tribe_paged=%d&tribe_event_display=photo' % pg_num)
        tree = html.fromstring(page.content)

        events = tree.xpath("//div[contains(@class,'type-tribe_events')]")
        notices = tree.xpath("//div[contains(@class,'tribe-events-notices')]/ul/li/text()")

        done = False

        if len(events) == 0:
            done = True
        else:
            for event in events:
                titles = event.xpath(".//h2[contains(@class,'tribe-events-list-event-title')]/a/text()")
                starts = event.xpath(".//span[contains(@class,'tribe-event-date-start')]/text()")
                stops = event.xpath(".//span[contains(@class,'tribe-event-time')]/text()")
                descriptions = event.xpath(".//div[contains(@class,'tribe-events-content')]/p/text()")
                links = event.xpath(".//a[contains(@class,'tribe-event-url')]/@href")
                #TODO use link to get more information and possibly use lxml function to replace relative urls to help following

                new_event = {}
                if len(titles) <= 0:
                    break #All items must have a title
                else:
                    new_event["title"] = titles[0].strip()

                if len(starts) > 0:
                    startstr = starts[0].strip()
                    try:
                        try_datetime = dateutil.parse(startstr, fuzzy=True)
                        output_datetime = datetime.strftime(try_datetime, '%m/%d/%Y %H:%M:%S')
                        new_event["start"] = output_datetime
                    except: #TODO don't just exept everything
                        print("Unable to parse start string '%s'" % startstr)
                    new_event["startstr"] = startstr

                if len(stops) > 0:
                    stopstr = stops[0].strip()
                    try:
                        start_time_str = new_event.get('start')
                        start_time = datetime.strptime(new_event['start'], '%m/%d/%Y %H:%M:%S') if start_time_str != None else None

                        try_datetime = dateutil.parse(stopstr, fuzzy=True, default=start_time)

                        output_datetime = datetime.strftime(try_datetime, '%m/%d/%Y %H:%M:%S')

                        new_event["stop"] = output_datetime
                    except: #TODO don't just exept everything
                        print("Unable to parse stop string '%s'" % stopstr)
                    new_event["stopstr"] = stopstr

                if len(descriptions) > 0:
                    new_event["description"] = descriptions[0].strip()

                if len(links) > 0:
                    new_event["link"] = links[0].strip()

                event_list.append(new_event)

        pg_num += 1

    extract_from_template("hartsvillesc.json")

    # json_text = json.dumps(event_list, indent=4)
    # with open(os.path.join(project_root(), "results", "hartsvillesc-test2.json"), "w+") as fp:
    #     fp.write(json_text)
