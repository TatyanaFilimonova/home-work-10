from collections import deque
from inspect import signature, getcallargs, getsource, unwrap
import time
import redis
import pickle
import ast

r = redis.Redis(
    host='localhost',
    port=6379, 
    )
r.flushdb()



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
            lru_cache =func_to_cache.__name__
            with open( 'LRU.txt', 'a') as log:
                log.write('---------------------------------------------\n') 
                log.write(f'Start caching for {lru_cache}\n')
                log.write('---------------------------------------------\n') 
            hash_=str(param_dict).encode()
            members = r.lrange(lru_cache,0,-1)
            if hash_ not in members:
                res = func_to_cache(*args, **kwargs)
                if len(members)<max_len:
                   r.lpush(lru_cache, hash_)
                else:
                    hash_to_del = r.rpop(lru_cache)
                    r.delete(pickle.dumps((hash_to_del, lru_cache)))
                    r.lpush(lru_cache, hash_)
                r.set(pickle.dumps((hash_, lru_cache)), pickle.dumps(res))
                return res
            else:
                if len(members)<max_len:
                    r.lrem(lru_cache,0, hash_)
                    r.lpush(lru_cache, hash_)
                return pickle.loads(r.get(pickle.dumps((hash_, lru_cache))))
        return get_args
    return wrapper


def LRU_cache_invalidate(*function_names : str):
    def wrapper(func_to_invalidate):
        with open( 'LRU.txt', 'a') as log:
            log.write(f'Start wrapper for {func_to_invalidate}\n')
        def get_args(*args, **kwargs):
            with open( 'LRU.txt', 'a') as log:
                log.write('---------------------------------------------\n')       
                res = func_to_invalidate(*args, **kwargs)
                log.write(f'Start invalidate for : {func_to_invalidate}\n')
                for function in function_names:
                    log.write(f'Looking for function: {function}\n')
                    param_hashes = r.lrange(function, 0, -1)
                    log.write(f'Find next parameters for this function: {param_hashes}\n')
                    if param_hashes!=[]:
                        log.write('find some cached data:\n')
                        for hash_ in param_hashes:
                            log.write(str(r.get(pickle.dumps((hash_, function))))[0:10]+'\n')
                            log.write('Try to delete it \n')
                            r.delete(pickle.dumps((hash_, function)))
                            if r.get(pickle.dumps((hash_, function))) == None:
                                log.write('OK\n')
                        r.ltrim(function, -1, -1)
                        r.lpop(function)
                log.write(f'Finish invalidate for : {func_to_invalidate}\n')
                log.write('---------------------------------------------\n')
                return res
        return get_args
    return wrapper

