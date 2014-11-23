# encoding: utf-8
from __future__ import with_statement
from distributedlock.memcachedlock import MemcachedLock

DEBUG = True
DEFAULT_TIMEOUT=60
DEFAULT_BLOCKING=True
DEFAULT_MEMCACHED_CLIENT=None
DEFAULT_LOCK_FACTORY=lambda key, timeout: MemcachedLock(key, DEFAULT_MEMCACHED_CLIENT, timeout)

__all__ = [ 'LockNotAcquiredError', 'distributedlock' ]

def _debug(msg):
    if DEBUG:
        print "LOCK:", msg


class LockNotAcquiredError(Exception):
    pass


class distributedlock(object):
    
    def __init__(self, key=None, lock=None, blocking=None, timeout=None):
        self.key = key
        self.lock = lock
        if blocking == None:
            self.blocking = DEFAULT_BLOCKING
        else:
            self.blocking = blocking

        if timeout == None:
            self.timeout = DEFAULT_TIMEOUT
        else:
            self.timeout = timeout
            
        if not self.lock:
            self.lock = DEFAULT_LOCK_FACTORY(self.key, self.timeout)
        
    # for use with decorator
    def __call__(self, f):
        if not self.key:
            self.key = "%s:%s" % (f.__module__, f.__name__)
        
        def wrapped(*args, **kargs):
            with self:
                return f(*args, **kargs)
        return wrapped
    
    # for use with "with" block
    def __enter__(self):
        if not (type(self.key) == str or type(self.key) == unicode) and self.key == '':
            raise RuntimeError("Key not specified!")
            
        if self.lock.acquire(self.blocking):
            _debug("locking with key %s" % self.key)
        else:
            raise LockNotAcquiredError()
            
        return self.lock
            
    def __exit__(self, type, value, traceback):
        _debug("releasing lock %s" % self.key)
        self.lock.release()
        


