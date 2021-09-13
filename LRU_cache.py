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
            param_dict = {}
            sig = signature(func_to_cache)
            bnd = sig.bind(*args, **kwargs)
            for param in sig.parameters.keys():
               if param in bnd.arguments:
                   param_dict[param] = bnd.arguments[param]
               else:
                   param_dict[param] = sig.parameters[param].default
            lru_cache =str(func_to_cache)
            hash_=str(param_dict).encode()
            members = r.lrange(lru_cache,0,-1)
            if hash_ not in members:
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
                if len(members)<max_len:
                    r.lrem(lru_cache,0, hash_)
                    r.lpush(lru_cache, hash_)
                return pickle.loads(r.get(hash_))
        return get_args
    return wrapper
