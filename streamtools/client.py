from requests import Session, Request
import ujson
import random

class Api:
  
  def __init__(self, url=None, **kw):
    self.url = url if url else 'localhost:7070'
    self.s = Session()

  def version(self):
    """
    Get the version of StreamTools
    """
    return self._http('GET', 'version')

  def library(self):
    """
    Get parameters for all available blocks.
    """
    return self._http('GET', 'library')

  def export_pattern(self):
    """
    Export the current state of the pattern.
    """
    return self._http('GET', 'export')

  def import_pattern(self, pattern):
    """
    Import a pattern from a dictionary object.
    """
    
    response = self._http('POST', 'import', data=pattern)
    
    if response['daemon'] != 'OK':
      raise ValueError('Error loading pattern')
    
    else:
      return True

  # TODO: Websocket support.
  # def ws(self, block_id):
  #   """
  #   Stream output from a block's websocket.
  #   """
  #   # construct url
  #   ws_url = 'ws://{}/ws/{}'.format(self.url, str(block_id))

  #   # create client object and connect
  #   ws = WebSocketClient(ws_url, protocols=['http-only', 'chat'])
  #   ws.connect()

  #   # yield output endlessly
  #   while True:
  #     m = ws.receive()
  #     if m is not None:
  #       yield ujson.dumps(m)
  #     else:
  #       break

  def stream(self, block_id):
    """
    Stream output from a block's httpstream.
    """

    resp = self._http("GET", 'stream/{}'.format(str(block_id)), json=False, stream=True)          
    
    # return an endless generator of objects.
    for line in resp.iter_lines():
    
      if line:
        yield ujson.loads(line)
    
      else:
        break

  def list_blocks(self):
    """
    List all blocks in current pattern.
    """
    return self._http("GET", 'blocks')

  def get_block(self, block_id):
    """
    Get a representation of a block.
    """
    resp = self._http("GET", 'blocks/{}'.format(block_id))
    
    if 'daemon' in resp and 'already exists' in resp['daemon']:
      raise ValueError('Block "{}" already exists'.format(block_id))
    
    return resp

  def create_block(self, block_id=None, **kw):
    """
    Create a block given an id, type, rule (dict), xpos and ypos.
    """
    
    # parse kwargs
    kw.setdefault('rule', None)
    assert('type' in kw)

    options = {
      'Type': kw.get('type'),   
      'Rule': kw.get('rule'),
      'Position' : {
        'X': kw.get('x_pos', random.choice(range(15, 900))),
        'Y': kw.get('y_pos', random.choice(range(15, 500)))
      }
    }
    # optional id, otherwise autogenerated
    if block_id:
      options['Id'] = block_id 

    resp = self._http("POST", 'blocks', data=options)
    
    if 'daemon' in resp and 'already exists' in resp['daemon']:
      raise ValueError('Block "{}" already exists'.format(block_id))
    
    return resp['Id']

  def delete_block(self, block_id):
    """
    Delete a block.
    """
    resp = self._http("DELETE", 'blocks/{}'.format(block_id))

    if 'daemon' in resp and 'does not exist' in resp['daemon']:
      raise ValueError('Block "{}" Does not exist'.format(block_id))
    
    return True

  def delete_blocks(self):
    """
    Delete all blocks
    """
    for block in self.list_blocks():
      self.delete_block(block['Id'])
    return True

  def update_block(self, block_id, rule):
    """
    A helpser for updating a block's rule.
    """
    return self.to_block_route(block_id, route='rule', msg=rule)

  def to_block_route(self, block_id, **kw):
    """
    Route a message to block's input route.
    """
    kw.setdefault('route', 'in')
    return self._http('POST', 'blocks/{}/{}'.format(block_id, kw['route']), data=kw['msg'])

  def from_block_route(self, block_id, **kw):
    """
    Get the current state of a blocks specified output route
    """
    kw.setdefault('route', 'rule')
    return self._http('GET', 'blocks/{}/{}'.format(block_id, kw['route']))

  def list_connections(self):
    """
    Get all current connections.
    """
    return self._http("GET", 'connections')

  def create_connection(self, conn_id=None, **kw):
    """
    Create a connection.
    """
    
    # check kwargs
    assert('from_id' in kw and 'to_id' in kw)

    options = {
      'FromId': kw['from_id'],
      'ToId': kw['to_id'],
      'ToRoute': kw.get('to_route', 'in')
    }

    # optionally set connection id
    if conn_id:
      options['conn_id'] = conn_id 

    resp = self._http("POST", 'connections', data=options)

    if 'daemon' in resp and 'does not exist' in resp['daemon']:
      raise ValueError('Block "{}" Does not exist'.format(conn_id))
    return resp['Id']

  def get_connection(self, conn_id):
    """
    Get a connection object
    """
    resp = self._http("GET", 'connections/{}'.format(conn_id))

    if 'daemon' in resp and 'does not exist' in resp['daemon']:
      raise ValueError('Connection "{}" Does not exist'.format(conn_id))
    return resp

  def delete_connection(self, conn_id):
    """
    Delete a connection.
    """
    resp = self._http("DELETE", 'connections/{}'.format(conn_id))
    if 'daemon' in resp and 'does not exist' in resp['daemon']:
      raise ValueError('Connection "{}" Does not exist'.format(conn_id))
    return True

  def delete_connections(self):
    """
    Delete all connections.
    """
    for conn in self.list_connections():
      self.delete_connection(conn['Id'])
    return True

  def from_connection_route(self, conn_id, route='last'):
    """
    Get the current state of a connection's specified route.
    """
    return self._http("GET", 'connections/{}/{}'.format(conn_id, route))

  def _http(self, method, path, json=True, **kw):
    """
    A wrapper for http requests to streamtools.
    """
    # serialize all incoming json
    if 'data' in kw:
      kw['data'] = ujson.dumps(kw['data'])

    # construct the url endpoint
    url = 'http://{}/{}'.format(self.url, path)

    # special handling for streaming kwarg
    stream = kw.pop('stream', False)

    # format the request
    req = Request(method, url, **kw)

    # execute
    resp = self.s.send(req.prepare(), stream=stream)

    # return
    if json:
      return ujson.loads(resp.content)
    return resp

