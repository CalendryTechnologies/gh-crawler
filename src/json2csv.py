'''
Converts json to csv 
'''

from os.path import join as pathjoin
import csv

from general import ASSETS_DIR, DEBUG

EMPTY_CSV = pathjoin(ASSETS_DIR, "upload", "_empty.csv")

with open(EMPTY_CSV, "r") as fp:
    EMPTY_CSV_HEADER = list(csv.reader(fp))[0] #Header items for empty csv template
    
EMPTY_CSV_REMAPPING = {
    'Subject' : '', 
    'Start Date' : '', 
    'Start Time' : '', 
    'End Date' : '', 
    'End Time' : '', 
    'All day event' : '', 
    'Reminder on/off' : '', 
    'Reminder Date' : '', 
    'Reminder Time' : '', 
    'Meeting Organizer' : '', 
    'Required Attendees' : '', 
    'Optional Attendees' : '', 
    'Meeting Resources' : '', 
    'Billing Information' : '', 
    'Categories' : '', 
    'Description' : 'description', 
    'Location' : '', 
    'Mileage' : '', 
    'Priority' : '', 
    'Private' : '', 
    'Sensitivity' : '', 
    'Show time as' : ''
}

def json2csv(json_input, csv_headers=EMPTY_CSV_HEADER, remapping=EMPTY_CSV_REMAPPING):
    '''
    Converts json-style list to csv-style list
    
    json-style list is list of dictionaries with named entries
    csv-style list is 2D list with headers at top and entries for each field in subsequent rows
    
    :param json_input: json-style list as discussed above to be converted
    :param csv_headers: list of items for first row in csv-style list (if None, all keys from json_input are used in alphabetical order)
    '''
    if csv_headers == None:
        csv_headers = set()
        for item in json_input:
            csv_headers.update(item.keys())
        csv_headers = sorted(list(csv_headers))
        
    csv_out = [csv_headers]
    
    for item in json_input:
        row = []
        for key in csv_headers:
            key = remapping.get(key) or key #remap keys if necessary (i.e. for pretty version vs json version
            row.append(item.get(key) or "") #add item if applicable else empty string
        csv_out.append(row)
    
    return csv_out

#TODO add csv2json reverse implementation if ever necessary

def main():
    pass #TODO add test cases

if __name__ == "__main__":
    main()
    