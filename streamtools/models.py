
from util import random_position
from client import Api


class Block(dict):
  
  def __init__(self, 
      id = None, 
      type = None, 
      rule = {},
      x_pos = random_position(20, 900),
      y_pos = random_position(20, 500),
      **kw
    ):
    super(Block ,self).__init__()
    self.itemlist = super(Block,self).keys()

    # initialize client.
    self._st = Api(url) if kw.get('url') else Api() 
    
    # set mappings.
    self.id = id
    self.__setitem__('Id', id) 
    
    self.type = type
    self.__setitem__('Type', type)  
    
    self.rule = rule
    self.__setitem__('Rule', rule)   
    
    self.position = {'X': x_pos, 'Y': y_pos}
    self.__setitem__('Position', self.position)


  def __setitem__(self, key, value):
       # TODO: what should happen to the order if
       #       the key is already in the dict       
      self.itemlist.append(key)
      super(Block,self).__setitem__(key, value)

  def __iter__(self):
      return iter(self.itemlist)
  
  def keys(self):
      return self.itemlist
  
  def values(self):
      return [self[key] for key in self]  
  
  def itervalues(self):
      return (self[key] for key in self)

  def build(self):
    """
    Build a block.
    """
    try:
      
      if self.id not in self._st.block_ids:
        
        return self._st.create_block(
          self.id, 
          type = self.type, 
          rule = self.rule, 
          x_pos = self.position['X'],
          y_pos = self.position['Y'] 
        )
      
      else:
        return self.id

    except ValueError:
      
      # already exists
      return self.id

  def __add__(self, obj):
    if isinstance(obj, Block):
      c =  Connection(from_id=self.id, to_id=obj.id)
      return c


class Connection(dict):
  
  def __init__(self, 
      id = None, 
      from_id = None, 
      to_id = {},
      to_route = "in",
      **kw
    ):

    super(Connection, self).__init__()
    self.itemlist = super(Connection, self).keys()

    self.id = id
    self.__setitem__('Id', id) 
    
    self.from_id = from_id
    self.__setitem__('FromId', from_id)  
    
    self.to_id = to_id
    self.__setitem__('ToId', to_id)   
    
    self.to_route = to_route
    self.__setitem__('ToRoute', to_route)   
  
    # initialize client.
    self._st = Api(url) if kw.get('url') else Api()   
  
  def __setitem__(self, key, value):
       # TODO: what should happen to the order if
       #       the key is already in the dict       
      self.itemlist.append(key)
      super(Connection, self).__setitem__(key, value)

  def __iter__(self):
      return iter(self.itemlist)
  
  def keys(self):
      return self.itemlist
  
  def values(self):
      return [self[key] for key in self]  
  
  def itervalues(self):
      return (self[key] for key in self)

  def build(self):
    """
    Build a Connection.
    """
    if self.id not in self._st.connection_ids:

      return self._st.create_connection(
        self.id, 
        from_id = self.from_id, 
        to_id = self.to_id, 
        to_route = self.to_route
      )

    else:
      return self.id


  def __add__(self, obj):
    
    if isinstance(obj, Block):
      c = Connection(from_id=self.id, to_id=obj.id)
      return c

    elif isinstance(obj, Pattern):
      obj.connections.append(self)
      return obj


class Pattern(dict):

  def __init__(self,
      connections = [],
      blocks = [],
      **kw
    ):

    super(Pattern, self).__init__()
    self.itemlist = super(Pattern, self).keys()

    self.connections = connections 
    self.__setitem__('Connections', connections)

    self.blocks = blocks
    self.__setitem__('Blocks', blocks)    

    # initialize client.
    self._st = Api(url) if kw.get('url') else Api()   

  def __setitem__(self, key, value):
       # TODO: what should happen to the order if
       #       the key is already in the dict       
      self.itemlist.append(key)
      super(Pattern, self).__setitem__(key, value)

  def __iter__(self):
      return iter(self.itemlist)
  
  def keys(self):
      return self.itemlist
  
  def values(self):
      return [self[key] for key in self]  
  
  def itervalues(self):
      return (self[key] for key in self)

  def build(self, overwrite=True):
    if overwrite:
      self._st.set_pattern({})
    self._st.set_pattern(self)

  def __add__(self, obj):
    
    if isinstance(obj, Block):
      self.blocks.append(obj)
      return self

    elif isinstance(obj, Connection):
      self.connections.append(obj)
      return self
