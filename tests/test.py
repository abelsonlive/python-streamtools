from unittest import TestCase

from streamtools import Api, Block, Connection, Pattern

st = Api()

class StreamToolsTests(TestCase):

  test_id = 'test-block'
  test_type = 'ticker'
  test_rule = {'Interval': '1s'}

  def test_block(self):
    try:
      st.delete_pattern()
    except:
      pass

    bid = st.create_block(self.test_id, type=self.test_type, rule=self.test_rule)
    assert bid == self.test_id
    
    blocks = st.list_blocks()
    print blocks
    assert blocks[0]['Id'] == self.test_id
    
    block = st.get_block(self.test_id)
    assert block['Rule']['Interval'] == self.test_rule['Interval']

    block = st.update_block(self.test_id, rule={'Interval': '5s'})
    print block
    block = st.get_block(self.test_id)
    print block['Rule']['Interval'], self.test_rule['Interval']
    assert block['Rule']['Interval'] != self.test_rule['Interval']

  def test_construction(self):
    try:
      st.delete_pattern()
    except:
      pass

    b = Block('1', 'ticker', {'Interval': '1s'})
    b2 = Block('2', 'tolog')
    
    p = Pattern()
    p += b 
    p += b2
   
    print st.get_pattern()
    
    c = (b + b2)
    c.to_route ='rule'
    p += c
    
    p.build()
    
    p = st.get_pattern()
    assert(p['Connections'][0]['ToRoute'] == c.to_route)
    
  def teardown(self):
    st.delete_block(self.test_id)

   