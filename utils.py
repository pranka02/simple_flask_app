import json
import sys
from functools import reduce

def json_parser(file):
    with open(file) as in_file: 
        data = json.load(in_file)
    return data

class nested_dict (dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value
    
def get_nested_dict(nested_dict, keys):
    return reduce(lambda d, k: d[k], keys, nested_dict)

def set_nested_dict(nested_dict, keys, value):
    get_nested_dict(nested_dict, keys[:])[keys[-1]] = value

def nested_dict_update(nested_dict, keys):
    if get_nested_dict(nested_dict, keys[:]):
        if not isinstance(get_nested_dict(nested_dict, keys[:]),list):
            get_nested_dict(nested_dict, keys[:]).update([keys[-1]])

def find_leaf_key(nested_dict,key,value,keys): 
    for k in keys:
        if k ==key:
            if nested_dict[key]:
                nested_dict[key].append(value)
            else:
                nested_dict[key] = value
        else:
            if isinstance(nested_dict[k],dict):
                keys =list(nested_dict[k].keys())
                find_leaf_key(nested_dict[k],key,value,keys)
        
def set_leaf_node(nested_dict,key,value):
    keys = list(nested_dict.keys())
    find_leaf_key(nested_dict,key,value,keys)
