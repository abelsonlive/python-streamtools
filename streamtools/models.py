import time 

from client import Api
import settings
from util import md5, random_position

def rand_x():
  return random_position(20, 900)

def rand_y():
  return random_position(20, 500)

class Block:
  
  def __init__(self, 
      id = None, 
      type = None, 
      rule = {},
      position = None,
      x_pos = rand_x(),
      y_pos = rand_y(),
      **kw
    ):
    
    # check for raw switch
    if not 'raw' in kw:
      
      self.id = id
      self.type = type
      self.rule = rule
      self.x_pos = x_pos
      self.y_pos = y_pos
    
    # parse raw stream tools block object.
    else:
      
      self.id = kw['raw'].get('Id', None)
      self.type = kw['raw'].get('Type', None)
      self.rule = kw['raw'].get('Rule', {})
      
      # position
      pos = kw['raw'].get('Position')
      if pos:
        self.x_pos = pos.get('X', rand_x())
        self.y_pos = pos.get('Y', rand_y())
      
      else:
        self.x_pos = rand_x()
        self.y_pos = rand_y()

    # initialize client.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)

    # refresh block
    self.refresh()

  @property 
  def position(self):
    return {'X': self.x_pos, 'Y': self.y_pos}

  @property 
  def raw(self):
    return {
      'Id': self.id,
      'Type': self.type,
      'Rule': self.rule,
      'Position': self.position
    }

  @property 
  def inblocks(self):
    block_ids = []
    for c in self._st.list_connections():
      if c['ToId'] == self.id:
        block_ids.append(c['FromId'])
    return block_ids

  @property 
  def outblocks(self):
    block_ids = []
    for c in self._st.list_connections():
      if c['FromId'] == self.id:
        block_ids.append(c['ToId'])
    return block_ids

  def stop(self):
    try:
      self._st.delete_block(self.id)
      return True
    except ValueError:
      return False

  def start(self):
    # create connection, reset id
    self.id = self._st.create_block(
                self.id, 
                type = self.type, 
                rule = self.rule, 
                x_pos = self.x_pos,
                y_pos = self.y_pos
              )  

  def exists(self):
    try:
      self._st.get_block(self.id)
      return True 
    except ValueError:
      return False

  def refresh(self, overwrite=True):
    if self.exists():
      self.stop()
    self.start()

  def send_to(self, route='rule', msg={}):
    return self._st.to_block_route(self.id, route=route, msg=msg)

  def recieve_from(self, route='out'):
    return self._st.from_block_route(self.id, route=route)

  def listen(self):
    return self._st.stream(self.id)

  def __add__(self, obj):

    if isinstance(obj, Block):
      c =  Connection(from_id=self.id, to_id=obj.id)
      return c

    elif isinstance(obj, Pattern):
      obj.blocks.append(self)
      return obj

  def __repr__(self):
    return "< Block.{} = {}, {} >"\
      .format(self.id, self.type, self.rule)


class Connection:
  
  def __init__(self, 
      id = None, 
      from_id = None, 
      to_id = None,
      to_route = "in",
      **kw
    ):

    if not 'raw' in kw:

      self.id = id
      self.from_id = from_id
      self.to_id = to_id  
      self.to_route = to_route

    else:
      self.id = kw['raw'].get('Id', None)
      self.from_id = kw['raw'].get('FromId', None)
      self.to_id = kw['raw'].get('ToId', None)
      self.to_route = kw['raw'].get('ToRoute', 'in')

    
    # initialize client.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)

    # build
    self.refresh()

  @property 
  def raw(self):
    """
    A mapping back to the raw representation of a Connection.
    """
    return {
      'Id': self.id,
      'FromId': self.from_id,
      'ToId': self.to_id,
      'ToRoute': self.to_route
    }

  def stop(self):

    """
    Remove the connection from the Api.
    """

    if self.id:
      try:
        self._st.delete_connection(self.id)
      except ValueError:
        pass

  def start(self):
    """
    Initialize the connection via the api
    """

    # create connection, reset id
    self.id = self._st.create_connection(
                self.id, 
                from_id = self.from_id, 
                to_id = self.to_id, 
                to_route = self.to_route
              )

  def refresh(self):
    """
    Update the api to current state of the object.
    """

    self.stop()
    self.start()

  def exists(self):
    try:
      self._st.get_connection(self.id)
      return True 
    except ValueError:
      return False

  def recieve_from(self, route="last"):
    msg = self._st.from_connection_route(self.id, route=route)
    return msg.pop('Last', None)

  def stream(self, interval=1, max_buffer=60):
    """
    Poll the last route for new results
    """
    
    msg_id = ''
    buffer = set()
    
    while True:
      
      # get msg, create id
      msg = self.recieve_from()

      if msg:
        msg_id = md5(msg)

        if msg_id not in buffer:
          buffer.add(msg_id)

          yield msg 

      if len(list(buffer)) >- max_buffer:
        buffer = set(list(buffer)[:-1])

      time.sleep(interval)


  def __add__(self, obj):
    """
    Logic for adding Blocks and Patterns.
    """
    if isinstance(obj, Block):
      return Connection(from_id=self.id, to_id=obj.id)

    elif isinstance(obj, Pattern):
      obj.connections.append(self)
      return obj

  def __repr__(self):
    return "< Connection.{} = Block.{} => Block.{}.{} >"\
      .format(self.id, self.from_id, self.to_id, self.to_route)


class Pattern:

  def __init__(self,
      connections = [],
      blocks = [],
      **kw
    ):
    
    self.connections = connections 
    self.blocks = blocks

    # initialize client.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)

    # global in/out blocks.
    self.inblock = None
    self.inroute = kw.get('inroute', 'in')
    self.outblock = None
    self.outroute = kw.get('outroute', 'out')
      
    if 'outblock' in kw:
      self.outblock = kw['outblock']

    elif 'inblock' in kw:
      self.inblock = kw['inblock']

    elif len(blocks):
      self.inblock = blocks[0]
      self.outblock = blocks[-1]

  @property 
  def raw(self):
    return {
      'Connections': [c.raw for c in self.connections],
      'Blocks': [b.raw for b in self.blocks]
    }
  
  def rm(self):

    # only delete blocks + connection associated 
    # with this pattern

    for c in self.connections:
      try:
        self._st.delete_connection(c.id)
      except ValueError:
        pass
      
      for b in self.blocks:
        try:
          self._st.delete_block(b.id)
        except ValueError:
          pass 

  def refresh(self, overwrite=True):
    
    if overwrite:
      self.rm()

    self._st.set_pattern(self.raw)

  def send_to(self, msg):
    inblock = [b for b in self.blocks if b.id == self.inblock][0]
    return self._st.to_block_route(inblock.id, route=self.inroute, msg=msg)

  def stream(self):
    outblock = [b for b in self.blocks if b.id == self.outblock][0]
    return self._st.from_block_route(outblock.id, route=self.outroute, msg=msg)

  def __add__(self, obj):
    
    if isinstance(obj, Block):
      self.blocks.append(obj)
      return self

    elif isinstance(obj, Connection):
      self.connections.append(obj)
      return self

  def __repr__(self):
    return "< Pattern = Connections => {}, Blocks => {} >"\
      .format(self.connections, self.blocks)

