python-streamtools
==================

A `python` wrapper for [`streamtools`](http://nytlabs.github.io/streamtools).

## Installation
```
pip install python-streamtools
```

## Tests
**NOTE** requires `streamtools` to be running on `localhost:7070`.
```
nosetests
```

## Usage 

### Low-level API Access
```python
import streamtools 

st = streamtools.Api()

ticker_id = st.create_block(type='ticker', rule={'Interval': '1s'})
log_id = st.create_block(type='tolog')

conn_id = st.create_connection(from_id=ticker_id, to_id=log_id)
print st.get_connection(conn_id)

for msg in st.stream(ticker_id):
  print msg
```

### Block, Connection, Pattern Construction:

```python
from streamtools import Api, Block, Connection, Pattern 

# init api
st = Api()

# init empty Pattern
p = Pattern()

# construct blocks
b1 = Block(type='ticker', rule={'Interval':'1s'})
b2 = Block(type='tolog')

print b1
print b2 

# construct a Connection explicity / implicitly
c = b1 + b2
print c 

# add connection to pattern
p += c
print p

# pattern exists on the api
print st.get_pattern()

# stream block output
for line in b1.stream():
  print line
```

## Notes
* Documentation is basic for now, refer to the [streamtools docs](http://nytlabs.github.io/streamtools/docs/), and the source code for full usage.
* `st.stream` seems to have significant latency.

## TODO

- [ ] Websocket support
- [ ] Custom Blocks which allow you to insert a python script, Would work via creating a series of blocks to query an internal api, pass input to a function, and pass output to another block.
- [ ] Figure out how to more elegantly specify custom `to_route` when adding two blocks together, eg:

```python
# right now 
c = b1 + b2 
c.to_route = 'rule'

#maybe:
c = b1 + b2('rule')
```
