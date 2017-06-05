'''
Contains filters for parsing data
'''

from datetime import datetime
import dateutil.parser as dateutil


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def filter_time(node, startstr_key='startstr', stopstr_key='endstr', **kwargs):
    '''
    Parses node keys to add 'start' and 'stop'
    
    :param node: dictionary to be modified (modified in place)
    :param kwargs: dictionary with node keys to use for startstr and stopstr
    '''
    startstr = node.get(startstr_key)
    stopstr = node.get(stopstr_key)
    start_datetime = None
    if startstr:
        #the node has a start string
        start_datetime = dateutil.parse(startstr, fuzzy=True)
        new_startstr = datetime.strftime(start_datetime, DATE_FORMAT)
        node['start_date'] = new_startstr
    if stopstr:
        stop_datetime = dateutil.parse(stopstr, fuzzy=True, default=start_datetime)
        new_stopstr = datetime.strftime(stop_datetime, DATE_FORMAT)
        node['end_date'] = new_stopstr
        
def get_filter(name):
    return globals().get("filter_" + name)
