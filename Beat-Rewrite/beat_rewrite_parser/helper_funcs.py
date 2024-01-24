
from helper_dataclasses import LocationAndLength as loc_len

# returns an inclusive range - might have to modify if it does not perform as expected
def rangeFromLocLen(loc_len):
    return range(loc_len.location, loc_len.length + 1)



    





