'''
Contains filters for parsing data
'''

from datetime import datetime
import dateutil.parser as dateutil


def filter_time(node, startstr_key='startstr', stopstr_key='stopstr', **kwargs):
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
        new_startstr = datetime.strftime(start_datetime, '%m/%d/%Y %H:%M:%S')
        node['start'] = new_startstr
    if stopstr:
        stop_datetime = dateutil.parse(stopstr, fuzzy=True, default=start_datetime)
        new_stopstr = datetime.strftime(stop_datetime, '%m/%d/%Y %H:%M:%S')
        node['stop'] = new_stopstr
        
def get_filter(name):
    return globals().get("filter_" + name)