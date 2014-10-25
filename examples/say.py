import os
from string import punctuation
from unidecode import unidecode
from streamtools import Plugin, Block

# define blocks
ws = Block('wiki-ws', 
  type='fromwebsocket', 
  rule={'url': 
  'ws://wikimon.hatnote.com:9000'})

log = Block('log', type='tolog')

# plugin to speak text
say = Plugin('say')

def say_main(body):
  text = body.get('summary', '')
  if text: 
    text = "".join([c for c in text if c not in punctuation])
    if text:
      os.system('say "%s"' % unidecode(text))
      yield {'clean_text': text}

say.main = say_main 

# define connections 
ws_to_say = (ws + say.in_block)
say_to_log = (say.out_block + log)

# attach plugin
say.attach()
