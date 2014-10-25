import time 

from client import Api
import settings
from util import md5, random_position

def rand_x():
  return random_position(20, 900)

def rand_y():
  return random_position(20, 500)

class Block:
 
  """
  A block is a StreamTools module,
  It can be connected with other blocks
  to form a StreamTools Connection
  """
 
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

    # initialize client + library.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)
    self._lib = self._st.library()

    # pull in existing block
    if self.is_attached():
      kw['raw'] = self._st.get_block(self.id)

    # check for raw switch
    if not 'raw' in kw:
      
      # assign in kwargs
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
      
      # parse position
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
   
    """
    The raw, api-friendly representation of this Block's position.
    """
   
    return {'X': self.x_pos, 'Y': self.y_pos}

  @property 
  def raw(self):

    """
    The raw, api-frienfly representation of this Block.
    """

    return {
      'Id': self.id,
      'Type': self.type,
      'Rule': self.rule,
      'Position': self.position
    }

  @property 
  def in_blocks(self):
    
    """
    The block ids this Block recieves messages from.
    """

    block_ids = []
    for c in self._st.list_connections():
      if c['ToId'] == self.id:
        block_ids.append(c['FromId'])
    return block_ids

  @property 
  def out_blocks(self):
    
    """
    The block ids this Block sends messages to.
    """
    
    block_ids = []
    for c in self._st.list_connections():
      if c['FromId'] == self.id:
        block_ids.append(c['ToId'])
    return block_ids

  @property 
  def in_routes(self):

    """
    This Block's available InRoutes
    """

    resp = self._lib.get(self.id, {})
    return resp.get('InRoutes', [])

  @property 
  def out_routes(self):
    
    """
    This Block's available OutRoutes
    """

    resp = self._lib.get(self.id, {})
    return resp.get('OutRoutes', [])

  @property 
  def query_routes(self):
    
    """
    This Block's available QueryRoutes
    """

    resp = self._lib.get(self.id, {})
    return resp.get('QueryRoutes', [])

  def attach(self):
   
    """
    Attach this Block to streamtools and update it's id.
    """
   
    # create block, reset id
    self.id = self._st.create_block(
                self.id, 
                type = self.type, 
                rule = self.rule, 
                x_pos = self.x_pos,
                y_pos = self.y_pos
              )  

  def detach(self):
    
    """
    Detach this Block from streamtools.
    """
    
    try:
      self._st.delete_block(self.id)
      return True
    
    except ValueError:
      return False

  def is_attached(self):
    
    """
    Check if this Block is attached to streamtools.
    """
    
    try:
      self._st.get_block(self.id)
      return True 
    
    except ValueError:
      return False

  def refresh(self, overwrite=True):
    
    """
    Check if this Block is attached to streamtools,
    if so, detach it first. Always attach it.
    """
    
    if self.is_attached():
    
      self.detach()

    self.attach()

  def send_to(self, **kw):
    
    """
    Send a msg to this Block's specified route.
    """
    
    # parse kwargs
    assert('msg' in kw)
    kw.setdefault('route', 'rule')

    return self._st.to_block_route(
            self.id, 
            route = kw['route'], 
            msg = kw['msg']
          )  

  def recieve_from(self, **kw):
    
    """
    Recieve a msg from this Block's specified route.
    """

    kw.setdefault('route', 'rule')
    return self._st.from_block_route(self.id, route=kw['route'])

  def listen(self):
    
    """
    Listen to the output channel of this Block.
    """
    
    return self._st.stream(self.id)

  def __add__(self, obj):
   
    """
    Methods for creating Connections 
    between this Block and other Blocks.
    """

    if isinstance(obj, Block):
      return Connection(from_id=self.id, to_id=obj.id)

  def __repr__(self):
    
    """
    Block display
    """
    
    return "< Block.{} = {}, {} >"\
      .format(self.id, self.type, self.rule)


class Connection:
  
  """
  A Connection is a linkage of two Blocks.
  """
  
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

    # pull in existing block if it exists.
    if self.is_attached():
      kw['raw'] = self._st.get_connection(self.id)

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
    
    """
    Blocks associated with this Connection
    """

    return [Block(self.from_id, _init=False), Block(self.to_id, _init=False)]

  def detach(self):

    """
    Remove the Connection from the Api.
    """

    if self.id:
      try:
        self._st.delete_connection(self.id)
      except ValueError:
        pass

  def attach(self):
    
    """
    Initialize the Connection via the api
    """

    # create connection, reset id
    self.id = self._st.create_connection(
                self.id, 
                from_id = self.from_id, 
                to_id = self.to_id, 
                to_route = self.to_route
              )

  def is_attached(self):

    """
    Check if this Connection is attached to streamtools,
    """

    try:
      
      self._st.get_connection(self.id)
      return True 
    
    except ValueError:
      
      return False

  def refresh(self):
   
    """
    Check if this Connection is attached to streamtools,
    if so, detach it first. Always attach it.
    """
    
    if self.is_attached():
      
      self.detach()

    self.attach()

  def recieve_from(self, route="last"):

    """
    Recieve a msg from this Block's specified route.
    """

    return self._st.from_connection_route(self.id, route=route)
  
  def listen(self, interval=1, max_buffer=60):
    
    """
    Poll the last route for new results
    """
    
    buffer = []
    
    while True:
      
      # get msg
      msg = self.recieve_from()
      msg = msg.pop('Last', None)

      if msg:

        # create msg hash
        msg_id = md5(msg)

        # check if the msg is new
        if msg_id not in buffer:
          buffer.append(msg_id)

          # yield new messages.
          yield msg 

      # trim buffer
      if len(buffer) >- max_buffer:
        buffer = [buffer[-1]]

      # rest
      time.sleep(interval)


  def __add__(self, obj):
    
    """
    Logic for adding Patterns + Connections.
    """
    
    if isinstance(obj, Pattern):
      obj.connections.append(self)
      obj.blocks.extend(self.blocks)
      return obj

    elif isinstance(obj, Connection):
      return Pattern(connections = [obj, self])

  def __repr__(self):

    """
    Connection display
    """

    return "< Connection.{} = Block.{} => Block.{}.{} >"\
      .format(self.id, self.from_id, self.to_id, self.to_route)


class Pattern:

  """
  A Pattern is a collection of one or more Connections 
  and the distinct Blocks associated with them.
  """

  def __init__(self,
      connections = [],
      **kw
    ):

    # listify
    if not isinstance(connections, list):
      connections = [connections]
    
    self.connections = connections 

    # lookup blocks
    self.blocks = [b for c in self.connections for b in c.blocks]

    # initialize client.
    self.url = kw.get('url', settings.STREAMTOOLS_URL)
    self._st = Api(self.url)

    # global in/out blocks.
    self.in_block = kw.get('in_block', None)
    self.in_route = kw.get('in_route', 'in')
    self.out_block = kw.get('out_block', None)
    self.out_route = kw.get('out_route', 'out')
      
  @property 
  def raw(self):

    """
    A mapping back to the raw representation of a Pattern.
    """
    
    return {
      'Connections': [c.raw for c in self.connections],
      'Blocks': [b.raw for b in self.blocks]
    }
  
  @property 
  def connection_ids(self):

    """
    A list of Connection ids associated with this Pattern.
    """
    
    return [c.id for c in self.connections]

  @property 
  def block_ids(self):

    """
    A list of Block ids associated with this Pattern.
    """

    return [b.id for b in self.blocks]

  def detach(self):

    """
    Detach this Pattern from streamtools. 
    Only delete Blocks + Connection associated 
    with this pattern.
    """

    # connections
    for c in self.connections:
      try:
        self._st.delete_connection(c.id)
      except ValueError:
        pass
    
    # blocks
    for b in self.blocks:
      try:
        self._st.delete_block(b.id)
      except ValueError:
        pass 

  def attach(self):

    """
    Attach this Pattern to streamtools. 
    """

    self._st.set_pattern(self.raw)

  def refresh(self, overwrite=True):

    """
    Refresh this Pattern. 
    """

    self.detach()
    self.attach()

  def send_to(self, msg):
    
    """
    Send a message to the specified in_route 
    of this pattern's specifed in_block
    """
    
    if not self.in_block:
      self.in_block = self.blocks[0]

    in_block = [b for b in self.blocks if b.id == self.in_block.id][0]
  
    return self._st.to_block_route(
            in_block.id, 
            route = self.in_route, 
            msg = msg
          )

  def listen(self):

    """
    Listen for messages from the out_route 
    of this pattern's specifed out_block
    """

    if not self.out_block:
      self.out_block = self.blocks[-1]

    out_block = [b for b in self.blocks if b.id == self.out_block.id][0]
    return self._st.stream(out_block.id)

  def __add__(self, obj):

    """
    Logic for adding Patterns + Connections.
    """

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

    """
    Pattern display
    """

    return "< Pattern = Connections => {}, Blocks => {} >"\
      .format(self.connections, self.blocks)

