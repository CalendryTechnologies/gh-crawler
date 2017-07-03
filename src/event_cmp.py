'''
Compares and merges events for use in combining uploads
'''

from datetime import datetime
from html import unescape
from difflib import SequenceMatcher


MATCHING_FIELDS = {"title", "description", "start_date", "end_date"} #items to use in comparison #TODO real values
FIELD_WEIGHTS = {"start_date" : 2, "end_date" : 2} #default weights #TODO real values

def str_cmp(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio() #TODO possibly quick_ratio or real_quick_ratio

def ev_cmp(ev1, ev2, match_fields=MATCHING_FIELDS, field_weights={}):
    diffs = []
    weighted_total = 0
    for k in match_fields:
        value1 = ev1.get(k)
        value2 = ev2.get(k)
        if value1 and value2:
            raw_diff = str_cmp(value1, value2)
            weight = field_weights.get(k) or 1
            diffs.append(raw_diff * weight)
            weighted_total += weight
            #TODO add some sort of special value diff because different dates appear similar as strings
        elif not value1 and not value2:
            #includes empty string to None comparison
            pass
        else:
            diffs.append(0) #possibly update for empty strings
            diffs += 1
    return sum(diffs) / weighted_total if weighted_total > 0 else 0 #default to zero if events have no usable fields
    
class EventList(list):
    def __init__(self, lst):
        super().__init__(lst)
        for event in lst:
            for k in event.keys():
                if isinstance(event[k], str):
                    event[k] = unescape(event[k])
      
    def by_datetime(self, start, stop=None, form="text"):
        if form == "datetime":
            pass
        elif form == "text":
            start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            stop = datetime.strptime(stop, "%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError("Unknown form %s" % form)
        
        if stop is None:
            def same_date(event):
                start_str = event.get("start_date")
                if not start_str:
                    return False
                else:
                    return datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S") == start
                
            return EventList(filter(same_date, self))
        
        else:
            def in_range(event):
                start_str = event.get("start_date")
                if not start_str:
                    return False
                else:
                    start_datetime = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    return start <= start_datetime <= stop
            
            return EventList(filter(in_range, self))
    
    def by_matching(self, compare_event, match_fields=MATCHING_FIELDS, threshold=1):
        if threshold == 1:
            #Only absolute matches
            def matches(event):
                for attribute in match_fields:
                    if event.get(attribute) != compare_event.get(attribute):
                        return False
                return True
            
            return EventList(filter(matches, self))
        else:
            #Fuzzy comparison matches based on percent difference
            def matches(event):
                return ev_cmp(event, compare_event, match_fields) > threshold
            
            return EventList(filter(matches, self))
        
    def to_dict(self):
        return {"events" : self}

def printEL(events):
    '''
    Prints EventList in a pretty form (for debugging)
    :parameter events: EventList to print
    '''
    if len(events) > 0:
        ret = "[\n"
        for ev in events:
            ret += strE(ev)
        ret += "]"
    else:
        ret = "[]"
    print(ret)

def strE(event):
    ret = "  %s (%s to %s)\n" % (
        event.get("title"),
        event.get("start_date"),
        event.get("end_date")
    )
    return ret

def main():
    #TODO put real test cases but for now, just use the ones already in existence
    import db_upload
    db_upload.main()

if __name__ == "__main__":
    main()
