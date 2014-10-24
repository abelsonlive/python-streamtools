import random
import hashlib 
import ujson

def random_position(min_=15, max_=900):
  return random.choice(range(min_, max_))

def md5(contents, json=True):
  if json:
    contents = ujson.dumps(contents)
  return hashlib.md5(contents).hexdigest()
