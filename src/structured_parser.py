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
import threading
import os
from os.path import join as pathjoin

import custom_filters
from general import PROJECT_ROOT


DEBUG = True

def extract_from_template(json_filename, debug=False):
    '''
    Reads json template file then extracts data according to its rules and writes it where specified
    '''
    template = get_template(pathjoin(PROJECT_ROOT, "templates", json_filename)) #filename in templates directory
    extract(template, debug=debug)

def get_template(json_filename):
    '''
    Reads from a file and gets the json template object

    :param json_filename: filename to open json from
    :return: returns json object from the file
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

def extract(rules_dict, debug=False):
    '''
    Extracts an entire set of data based on a rules dictionary
    '''
    annotations, processes = partition_rules(rules_dict)

    output_dir = pathjoin(PROJECT_ROOT, "results", (annotations.get("@output_dir") or ".")) #get output_dir or use blank relative path #TODO possibly need to use . for relative location
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for process_key in processes:
        #loop through each process and complete it
        #TODO do this with threading/multiprocessing since they are all separate  #TODO maybe not because of end condition (see later)
        process_rules = rules_dict[process_key]
        process_output = pathjoin(output_dir, process_key + ".json") #save to process_key with .json extension

        thread = threading.Thread(target=extract_process, args=(process_rules, process_output, {}, debug))
        thread.start()

        #extract_process(process_rules, process_output, debug=debug) #extract from the individual process

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

def extract_process(rules_dict, output_file, variables={}, debug=False):
    '''
    Extracts from a single process in the template and outputs it to a file

    :param rules_dict: Inner dictionary from the specific process
    :param output_file: Filename to output results to in json format
    :return: returns True if the extraction was successful else False
    '''
    annotations = partition_rules(rules_dict)[0] #get annotations and misc (there shouldn't be anything without annotation)

    new_variables, new_lists = get_variables(annotations)
    variables.update(new_variables) #add variables to the dictionary
    variables.update({k:v[0] for k,v in new_lists.items() if len(v) > 0}) #put first value of each list in dictionary

    url = annotations.get("@url")
    if url == None: return False #url is required for process

    results = {}

    done = False
    while not done:
        for var in variables.items():
            temp_url = url.replace("{$%s}" % var[0], str(var[1])) #replace any instance of variables in url

            single_result = extract_node_from_url(temp_url, rules_dict, debug=debug) #TODO we can't use threading for this because the return must be used to determine if it changed anything
            if DEBUG: print("extracted from %s" % temp_url)

        #nothing was found at the specified url
        if len(single_result) <= 0:
            done = True

        #incremement numeric variable
        for var_key in new_variables.keys():
            variables[var_key] += 1

        #increment list variables and determine if it is the end of the list
        for list_key in new_lists.keys():
            cur_val = variables[list_key]
            cur_index = new_lists[list_key].index(cur_val)
            if cur_index == len(new_lists[list_key]) - 1:
                done = True #this is the last element in the list
            else:
                variables[list_key] = new_lists[list_key][cur_index+1]

        #add single result to the list
        for node_name in single_result.keys():
            if node_name not in results.keys():
                results[node_name] = [] #create the node name if it doesn't exist
            results[node_name].extend(single_result[node_name]) #extend the node value list

    #write the results to file
    json_text = json.dumps(results, indent=4, ensure_ascii=False) #later we can take out indent which makes it readable
    with open(output_file, "w+") as fp:
        fp.write(json_text)

    return True #if nothing went wrong, it's a success

def extract_node_from_url(url, rules_dict, debug=False):
    '''
    Extracts a complete node from a document via ruled dictionary from url

    :param url: String url to pull from
    :rules_dict: dictionary with node rules
    :param output_file: filename to write to (absolute)
    :param variables: dictionary of variables to use
    :return: Returns True if the query was nonempty else False
    '''
    page = requests.get(url)
    tree = html.fromstring(page.content)
    tree.make_links_absolute(url) #make sure href links are absolute for following later

    return extract_node(tree, rules_dict, debug=debug)[0] #extracts the base node
    
def extract_node(doc_root, rules_dict, debug=False):
    '''
    Extracts a complete node from a document via a ruled dictionary

    :param doc_root: document root element (created by lxml.html.fromstring())
    :rules_dict: dictionary with node rules
    :return: Returns success rate boolean
    '''
    annotations, elements = partition_rules(rules_dict) #elements contain only xpath to pull from

    node_xpath = rules_dict.get("@xpath") or "." #gets xpath of node or uses relative location else

    nodes = {} #nodes dicionary contains each node
    follows = [] #node to follow for more info
    filters = [] #filters to apply in format (type, kwargs)
    for annotation in annotations.items():
        if annotation[0].startswith("@node:"):
            nodes[annotation[0].replace("@node:", "")] = annotation[1]
        if annotation[0] == "@follow":
            follows.append(annotation[1])
        if annotation[0].startswith("@filter"):
            filters.append((annotation[0].replace("@filter:", ""), annotation[1]))

    node_roots = doc_root.xpath(node_xpath) #gets all nodes
    node_results = []

    #get all non-nodes from the node
    for node_root in node_roots:
        output = {} #single node output will be extended with each non-annotation

        for name, element_xpath in elements.items():
            results = node_root.xpath(element_xpath)
            if len(results) > 0:
                output[name] = results[0].strip()

        #following follow tags
        for follow_rule in follows:
            follow_link_xpath = follow_rule.get("@xpath") #TODO handle when @xpath tag DNE
            follow_rule = {key:follow_rule[key] for key in follow_rule if key != "@xpath"} #temporarily remove the xpath tag

            follow_links = node_root.xpath(follow_link_xpath)
            follow_link = follow_links[0] #TODO handle case when xpath DNE

            follow_results = extract_node_from_url(follow_link, follow_rule, debug=debug)
            output.update(follow_results)

        #collecting internal nodes
        for node_name, node_rules in nodes.items():
            output[node_name] = extract_node(node_root, node_rules, debug=debug)

        for filter_name, filter_kwargs in filters:
            #custom_filter = filter_dict.get(filter_name)
            custom_filter = custom_filters.get_filter(filter_name)
            if filter:
                #filter is not None
                custom_filter(output, **filter_kwargs)

        node_results.append(output) #add this node instance to the total list of results

    return node_results

if __name__ == "__main__":
    extract_from_template("hartsvillesc.json")

