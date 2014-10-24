python-streamtools
==================

A `python` wrapper for [`streamtools`](http://nytlabs.github.io/streamtools).

## Installation
```
pip install python-streamtools
```

## Usage 
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

## Notes
* Documentation is basic for now, refer to the [streamtools docs](http://nytlabs.github.io/streamtools/docs/), and the source code for full usage.
* `st.stream` seems to have significant latency.

## TODO

- [ ] Websocket support
- [ ] Custom Blocks which allow you to insert a python script, Would work via creating a series of blocks to query an internal api, pass input to a function, and pass output to another block.
- [ ] Dynamic creation of patterns via Block and Connection objects, eg:

```python
from streamtools import Block, Stream

ticker = Block('ticker', {'Interval': '1s'})
logger = Block('tolog', {'Interval': '1s'})

conn = ticker + logger 

s = Stream(ticker.id)
for line in s.listen():
  print line
```