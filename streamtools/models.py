
from util import random_position
from client import Api


class Block:
  
  def __init__(self, 
      id = None, 
      type = None, 
      rule = {},
      position = None,
      x_pos = random_position(20, 900),
      y_pos = random_position(20, 500),
    ):
    
    self.id = id
    self.type = type
    self.rule = rule
    self._set_position(position, x_pos, y_pos)

  def _set_position(self, position=None, x_pos = None, y_pos = None):
    
    if not position:
      
      # parse position
      x_pos = x_pos if x_pos else random_position()
      y_pos = y_pos if y_pos else random_position()
      position = {'X': x_pos, 'Y': y_pos}

    self.position = position

  @property 
  def raw(self):
    return {
      'Id': self.id,
      'Type': self.type,
      'Rule': self.rule,
      'Position': self.position
    }

  def __add__(self, obj):
    if isinstance(obj, Block):
      c =  Connection(from_id=self.id, to_id=obj.id)
      return c

  def __repr__(self):
    return "< Block {} / {} >"\
      .format(self.id, self.type)


class Connection:
  
  def __init__(self, 
      id = None, 
      from_id = None, 
      to_id = None,
      to_route = "in"
    ):

    self.id = id
    self.from_id = from_id
    self.to_id = to_id  
    self.to_route = to_route
  
  
  @property 
  def raw(self):
    return {
      'Id': self.id,
      'FromId': self.from_id,
      'ToId': self.to_id,
      'ToRoute': self.to_route
    }

  def __add__(self, obj):
    
    if isinstance(obj, Block):
      c = Connection(from_id=self.id, to_id=obj.id)
      return c

    elif isinstance(obj, Pattern):
      obj.connections.append(self)
      return obj

  def __repr__(self):
    return "< Connection {} / Block {} => Block {}>"\
      .format(self.id, self.from_id, self.to_id)


class Pattern:

  def __init__(self,
      connections = [],
      blocks = [],
      **kw
    ):
    
    self.connections = connections 
    self.blocks = blocks

    # initialize client.
    self._st = Api(url) if kw.get('url') else Api()   

  @property 
  def raw(self):
    return {
      'Connections': [c.raw for c in self.connections],
      'Blocks': [b.raw for b in self.blocks]
    }

  def build(self, overwrite=True):
    if overwrite:
      self._st.delete_pattern()
    self._st.set_pattern(self.raw)

  def __add__(self, obj):
    
    if isinstance(obj, Block):
      self.blocks.append(obj)
      return self

    elif isinstance(obj, Connection):
      self.connections.append(obj)
      return self

  def __repr__(self):
    return "< Pattern => Connections = {} / Blocks = {} >"\
      .format(self.connections, self.blocks)

