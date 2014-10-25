import os
from string import punctuation
from unidecode import unidecode
from streamtools import Plugin, Block

# create blocks
ws_block = Block('wiki-ws', 
  type='fromwebsocket', 
  rule={'url': 
  'ws://wikimon.hatnote.com:9000'})

log_block = Block('log', type='tolog')

# create plugin to speak text
say = Plugin('say')

def say_main(body):
  text = body.get('summary', '')
  if text: 
    text = "".join([c for c in text if c not in punctuation])
    if text:
      print len(text)
      yield {'clean_text': text}

say.main = say_main 

# define connections 
print ws_block + say.in_block
print say.out_block + log_block

# attach plugin
say.attach()
