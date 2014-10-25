from unittest import TestCase

import streamtools as st
api = st.Api()

class StreamToolsTests(TestCase):

  test_id = 'test-block'
  test_type = 'ticker'
  test_rule = {'Interval': '1s'}

  def test_block(self):
    try:
      api.delete_pattern()
    except:
      pass

    bid = api.create_block(self.test_id, type=self.test_type, rule=self.test_rule)
    assert bid == self.test_id
    
    blocks = api.list_blocks()
    print blocks
    assert blocks[0]['Id'] == self.test_id
    
    block = api.get_block(self.test_id)
    assert block['Rule']['Interval'] == self.test_rule['Interval']

    block = api.update_block(self.test_id, rule={'Interval': '5s'})
    print block
    block = api.get_block(self.test_id)
    print block['Rule']['Interval'], self.test_rule['Interval']
    assert block['Rule']['Interval'] != self.test_rule['Interval']

  def test_construction(self):
    try:
      api.delete_pattern()
    except:
      pass

    b = st.Block('1', type='ticker', rule={'Interval': '1s'})
    b2 = st.Block('2', 'tolog')    
    c = b + b2
    p = st.Pattern()
    p += c

    p = st.get_pattern()
    assert(p['Connections'][0]['ToRoute'] == c.to_route)
    
  def teardown(self):
    api.delete_block(self.test_id)

   