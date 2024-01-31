import re
import uuid
from uuid import uuid4

from line import Line, LineType
import helper_funcs as hf
from note import Note

class StaticPostParser:
    """
    This is responsible for handling [[Notes]] and /* Boneyards */

    Specifically, identifies the starting location and length of each Note or Boneyard.
    """
    
    @classmethod
    def get_open_and_close_index_sets_from_document_string(cls,
                                            document: str, 
                                            open_pattern: str, 
                                            close_pattern: str) -> dict[int, int]:
        """
        Given an open regex pattern and a close regex pattern,
        returns a `tuple`: (`opens`: `set`, `closes`: `set`) 
        which holds the indexes of the open and close patterns.
        """
        
        open_cmp_ptrn = re.compile(open_pattern, re.IGNORECASE)

        close_cmp_ptrn = re.compile(close_pattern, re.IGNORECASE)

        opens: set = cls.get_all_indexes_of_chars_in_string(open_cmp_ptrn, document)        # indexes for every opener location
        closes: set = cls.get_all_indexes_of_chars_in_string(close_cmp_ptrn, document)        # indexes for every closer


        return (opens, closes)


    @staticmethod
    def get_all_indexes_of_chars_in_string(pattern_to_find: str, string: str) -> set:

        indices_obj = re.finditer(pattern=pattern_to_find, string=string)
        index_set: list = []
        for index in indices_obj:
            #print(index.start(), string[index.start():index.start()+10])
            index_set.append(index.start())
        
        return index_set
    
    # def _is_index_in_invisible_line(self):
    #     # while searching for each set of indexes, check if it is part of a synopse or a section.
    #     # Find the `Line` which contains the index 
    #     if index in hf.range_from_loc_len(lines[0].get_loc_len):
    #         return True
    #     return False

        # If it is part of a synopse or section, don't add it to the set.

    

    