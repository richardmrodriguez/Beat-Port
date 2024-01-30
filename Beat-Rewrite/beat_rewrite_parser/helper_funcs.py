
from helper_dataclasses import LocationAndLength as loc_len

# returns an inclusive range - might have to modify if it does not perform as expected
def range_from_loc_len(loc_len):
    return range(loc_len.location, loc_len.length + 1)

def only_uppercase_until_parenthesis(text: str): # Might want to move this func to helper_funcs to be cleaner
        until_parenthesis = text.split("(")[0]
        if (
            until_parenthesis == until_parenthesis.upper()
            and len(until_parenthesis) > 0
            
            ):
            return True
        else:
            return False

    





