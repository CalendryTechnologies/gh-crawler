'''
Compares and merges events for use in combining uploads
'''

from datetime import datetime


MATCHING_FIELDS = {"title", "description", "start_date", "end_date"} #TODO real values

def ev_cmp(ev1, ev2):
    pass #TODO lots of implementation here)

class EventList(list):
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
    
    def by_matching(self, compare_event, match_fields=MATCHING_FIELDS):
        def matches(event):
            for attribute in match_fields:
                if event.get(attribute) != compare_event.get(attribute):
                    return False
            return True
        
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
