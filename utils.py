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
                nested_dict[key] = [value]
        else:
            if isinstance(nested_dict[k],dict):
                keys =list(nested_dict[k].keys())
                find_leaf_key(nested_dict[k],key,value,keys)
        
def set_leaf_node(nested_dict,key,value):
    keys = list(nested_dict.keys())
    find_leaf_key(nested_dict,key,value,keys)

def make_nested_dictionary(data,all_levels,key_levels):
    leaf_levels = list(set(all_levels)-set(key_levels))
    nd = nested_dict()
    for flat_dict in data:
        level_keys =[]
        diff_keys ={}
        for level in key_levels:
            level_keys.append(flat_dict[level])
            for lf in leaf_levels:
                 diff_keys[lf] =flat_dict[lf]
                
            nested_dict_update(nd,level_keys)
            if diff_keys:
                set_leaf_node(nd,level_keys[-1],diff_keys)
    return nd