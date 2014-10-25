import os
from string import punctuation
from unidecode import unidecode
from streamtools import Plugin, Block

import gevent 
import gevent.monkey 
gevent.monkey.patch_all()

# create blocks
ws_block = Block('wiki-ws', 
  type='fromwebsocket', 
  rule={'url': 
  'ws://wikimon.hatnote.com:9000'})

# create histogram block 
hist_block = Block('hist-1', 
  type='histogram', 
  rule={"Path": ".word", 
  "Window": "1h0m0s"})

# create ticker block 
ticker_block = Block('ticker-1', 
  type='ticker', 
  rule={'Interval': '1s'})

# create log block.
log_block = Block('log', type='tolog')

# create plugin to tokenize text
tokenize = Plugin('tokenize')

def tokenize_main(body):
  text = body.get('summary', '')
  if text: 
    text = "".join([c for c in text if c not in punctuation])\
                .lower()\
                .strip()

    for word in text.split():
      word = word
      if word:
        yield {'word': word}

tokenize.main = tokenize_main 

# # create plugin to Filter text
# filter_block = Plugin('plugin-filter')

# def filter_block_main(body):
#   print body
#   for obj in body.get('Histogram', []):
#     if body.get('Count', 1) > 1:
#       yield body

# filter_block.main = filter_block_main


# define connections 
c1 = ws_block + tokenize.in_block
print c1 
c2 = tokenize.out_block + hist_block
print c2
c3 = ticker_block + hist_block 
c3.to_route = 'poll'
c3.refresh()
print c3 
c4 = hist_block + log_block
# print c4 
# c5 = filter_block.out_block + log_block
# print c5

tokenize.attach()
