import hashlib
import json
from datetime import datetime


def get_score(store, phone, email, birthday=None, gender=None, first_name=None, last_name=None):
    key_parts = [
        first_name or "",
        last_name or "",
        phone or "",
        datetime.strptime(birthday, "%d.%m.%Y").date().strftime("%Y%m%d") if birthday is not None else "",
    ]
    key = "uid:" + hashlib.md5("".join(str(key) for key in key_parts).encode('utf8')).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    value = store.cache_get(key)
    score = json.loads(value) if value else 0
    if score:
        return score
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(store, cid):
    r = store.get("i:%s" % cid)
    if r:
        return json.loads(r)
    else:
        raise ValueError('Not found in store')
