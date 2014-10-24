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
from streamtools import Api, Block, Pattern 

# init api
st = Api()

# init empty Pattern
p = Pattern()

# blocks
b1 = Block('test', 'ticker', {'Interval':'1s'})
b2 = Block('test-3', 'tolog')

# add blocks to pattern
p += b1 
p += b2 

# add connection to pattern
p += (b1 + b2)

# alternatively construct a pattern
c = Connection(from_id=b1.id, to_id=b2.id, to_route='in')

# checf it patterne exists yet
print st.get_pattern()

# explicity build pattern
p.build()

# there it is
print st.get_pattern()

# stram to output
for line in st.stream(b1.id):
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
