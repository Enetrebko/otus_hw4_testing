import unittest
from store import Store
from time import sleep
import scoring
from unittest.mock import patch


class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.store = Store()

    def test_get(self):
        self.store.set('key', 5)
        value = self.store.get('key')
        self.assertEqual(value, b'5')

    def test_cache_get(self):
        self.store.cache_set('key', 5)
        value = self.store.cache_get('key')
        self.assertEqual(value, b'5')

    def test_store_time(self):
        self.store.cache_set('key', 5, store_time=3)
        sleep(3)
        value = self.store.cache_get('key')
        self.assertEqual(value, None)

    def test_score_wo_redis(self):
        store = Store(host="128.128.128.128")
        value = scoring.get_score(store, phone="79175002040", email="stupnikov@otus.ru")
        self.assertEqual(value, 3)

    def test_interests_wo_redis(self):
        store = Store(host="128.128.128.128")
        with self.assertRaises(ConnectionError):
            scoring.get_interests(store, 1)
