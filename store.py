import redis
import logging
from functools import wraps
from time import sleep
from settings.redis_config import *


def reconnect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for i in range(args[0].attempts):
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                logging.info(f'{e}, attempt_no: {i}')
                sleep(RETRY_DELAY)
            else:
                return value
        raise ConnectionError
    return wrapper


class Store:
    def __init__(self, host=HOST, port=PORT):
        self.store = redis.Redis(host=host,
                                 port=port,
                                 socket_timeout=SOCKET_TIMEOUT,
                                 socket_connect_timeout=SOCKET_CONNECT_TIMEOUT)
        self.attempts = ATTEMPTS

    @reconnect
    def cache_get(self, key):
        try:
            return self.store.get(key)
        except redis.exceptions.ConnectionError:
            return

    @reconnect
    def cache_set(self, key, value, store_time=None):
        try:
            self.store.set(key, value)
            if store_time:
                self.store.expire(key, store_time)
        except redis.exceptions.ConnectionError:
            pass

    @reconnect
    def get(self, key):
        return self.store.get(key)


    @reconnect
    def set(self, key, value):
        self.store.set(key, value)
