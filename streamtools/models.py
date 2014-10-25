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

    # get id 
    self.id = id

    # initialize client.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)

    # pull in existing block
    if self.exists():
      kw['raw'] = self._st.get_block(self.id)

    # check for raw switch
    if not 'raw' in kw:
      
      self.id = id
      self.type = type
      self.rule = rule
      self.x_pos = x_pos
      self.y_pos = y_pos
    
    # parse raw stream tools block object.
    else:
      self.id = kw['raw'].get('Id', id)
      self.type = kw['raw'].get('Type', type)
      self.rule = kw['raw'].get('Rule', rule)
      
      # position
      pos = kw['raw'].get('Position')
      if pos:
        self.x_pos = pos.get('X', rand_x())
        self.y_pos = pos.get('Y', rand_y())
      
      else:
        self.x_pos = rand_x()
        self.y_pos = rand_y()

    if kw.get('_init', True):
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
  def in_blocks(self):
    block_ids = []
    for c in self._st.list_connections():
      if c['ToId'] == self.id:
        block_ids.append(c['FromId'])
    return block_ids

  @property 
  def out_blocks(self):
    block_ids = []
    for c in self._st.list_connections():
      if c['FromId'] == self.id:
        block_ids.append(c['ToId'])
    return block_ids

  @property 
  def in_routes(self):
    resp = self._st.library()
    resp = resp.get(self.id, {})
    return resp.get('InRoutes', []]

  @property 
  def out_routes(self):
    resp = self._st.library()
    resp = resp.get(self.id, {})
    return resp.get('OutRoutes', []]

  @property 
  def query_routes(self):
    resp = self._st.library()
    resp = resp.get(self.id, {})
    return resp.get('QueryRoutes', []]

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
      return Connection(from_id=self.id, to_id=obj.id)

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
    # get id 
    self.id = id

    # initialize client.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)

    # pull in existing block
    if self.exists():
      print here
      kw['raw'] = self._st.get_block()

    if not 'raw' in kw:

      self.from_id = from_id
      self.to_id = to_id  
      self.to_route = to_route

    else:
      self.id = kw['raw'].get('Id', id)
      self.from_id = kw['raw'].get('FromId', from_id)
      self.to_id = kw['raw'].get('ToId', to_id)
      self.to_route = kw['raw'].get('ToRoute', to_route)

    if kw.get('_init', True):
      # refresh block
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

  @property 
  def blocks(self):
    return [Block(self.from_id, _init=False), Block(self.to_id, _init=False)]

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
    return self._st.from_connection_route(self.id, route=route)
    
  def listen(self, interval=1, max_buffer=60):
    """
    Poll the last route for new results
    """
    
    msg_id = ''
    buffer = []
    
    while True:
      
      # get msg, create id
      msg = self.recieve_from()
      msg = msg.pop('Last', None)

      if msg:
        msg_id = md5(msg)

        if msg_id not in buffer:
          buffer.append(msg_id)

          yield msg 

      if len(list(buffer)) >- max_buffer:
        buffer = [buffer[-1]]

      time.sleep(interval)


  def __add__(self, obj):
    """
    Logic for adding Blocks and Patterns.
    """
    if isinstance(obj, Block):
      return Connection(from_id=self.id, to_id=obj.id)

    elif isinstance(obj, Pattern):
      obj.connections.append(self)
      self.blocks.extend(self.blocks)
      return obj

    elif isinstance(obj, Connection):
      return Pattern(connections = [obj, self])

  def __repr__(self):
    return "< Connection.{} = Block.{} => Block.{}.{} >"\
      .format(self.id, self.from_id, self.to_id, self.to_route)


class Pattern:

  def __init__(self,
      connections = [],
      **kw
    ):
    
    self.connections = connections 
    self.blocks = [b for c in self.connections for b in c.blocks]

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

    elif len(self.blocks):
      self.inblock = self.blocks[0]
      self.outblock = self.blocks[-1]

  @property 
  def raw(self):
    return {
      'Connections': [c.raw for c in self.connections],
      'Blocks': [b.raw for b in self.blocks]
    }
  
  @property 
  def connection_ids(self):
    return [c.id for c in self.connections]

  @property 
  def block_ids(self):
    return [b.id for b in self.blocks]

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
    
    if isinstance(obj, Connection):
      
      # only add new conections + blocks to Pattern
      if obj.id not in self.connection_ids:
        self.connections.append(obj)
      
      for b in obj.blocks:
        if b.id not in self.block_ids:
          self.blocks.append(b)

      return self

    elif isinstance(obj, Pattern):
      
      # only add new conections + blocks to Pattern
      for c in obj.connections:
        if c.id not in obj.connection_ids:
          self.connections.append(c)
      
      for b in obj.blocks:
        if b.id not in self.block_ids:
          self.blocks.append(b)

      return self

  def __repr__(self):
    return "< Pattern = Connections => {}, Blocks => {} >"\
      .format(self.connections, self.blocks)

