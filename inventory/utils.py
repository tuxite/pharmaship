# -*- coding: utf-8; -*-
import datetime

def req_qty_element(element, req_qty_list):
    """ Returns the required quantity of an element from the allowance list and required quantities list."""
    # Required quantity
    maximum = [0,]
    additional = 0
    for item in req_qty_list:
        if item.base == element:
            if item.allowance.additional == True:
                additional += item.required_quantity
            else:
                maximum.append(item.required_quantity)
    return additional + max(maximum)
    
def delay(delta):
    """Returns the date including a delay in days."""
    return datetime.date.today() + datetime.timedelta(days=delta)
    
# Functions
def slicedict(d, s):
    return {k:v for k,v in d.iteritems() if k.startswith(s)}