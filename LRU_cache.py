from collections import deque
from inspect import signature, getcallargs
import time
import redis
import pickle
import ast

r = redis.Redis(
    host='localhost',
    port=6379, 
    )


def LRU_cache(max_len):
    def wrapper(func_to_cache):
        def get_args(*args, **kwargs):
            print("Was it cached?")
            param_dict = {}
            args_dict = getcallargs(func_to_cache, *args, *kwargs)
            sig = signature(func_to_cache)
            bnd = sig.bind(*args, **kwargs)
            for param in sig.parameters.keys():
               if param in bnd.arguments:
                   param_dict[param] = bnd.arguments[param]
               else:
                   param_dict[param] = sig.parameters[param].default
            print(param_dict)       
            lru_cache ='cache'
            hash_=str(param_dict).encode()
            members = r.lrange(lru_cache,0,-1)
            print(members)
            if hash_ not in members:
                print("No")
                res = func_to_cache(*args, **kwargs)
                if len(members)<max_len:
                   r.lpush(lru_cache, hash_)
                else:
                    hash_to_del = r.rpop(lru_cache)
                    r.delete(hash_to_del)
                    r.lpush(lru_cache, hash_)
                r.set(hash_, pickle.dumps(res))
                return res
            else:
                print("Yes")
                if len(members)<max_len:
                    r.lrem(lru_cache,0, hash_)
                    r.lpush(lru_cache, hash_)
                return pickle.loads(r.get(hash_))
        return get_args
    return wrapper

'''@LRU_cache (max_len =5)
def cap_str(strings, descending = True, mult = 1, capital = True):
    time.sleep(2)
    res = []    
    for s in strings:
        res.append(s.upper()*mult)
    return sorted(res, reverse = descending)     

if __name__='__mailn__':
    str_list = ['a','b','a','c','b','d','e','g']
    r.flushall()    
    for st in str_list:
        print(cap_str(st, False))
'''    
