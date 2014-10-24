from unittest import TestCase

import streamtools

st = streamtools.Api()

class StreamToolsTests(TestCase):

  test_id = 'test-block'
  test_type = 'ticker'
  test_rule = {'Interval': '1s'}

  def test_block(self):
    try:
      st.delete_block(self.test_id)
    except:
      pass

    bid = st.create_block(self.test_id, type=self.test_type, rule=self.test_rule)
    assert bid == self.test_id
    
    blocks = st.list_blocks()
    assert blocks[0]['Id'] == self.test_id
    
    block = st.get_block(self.test_id)
    assert block['Rule']['Interval'] == self.test_rule['Interval']

    block = st.update_block(self.test_id, rule={'Interval': '5s'})
    print block
    block = st.get_block(self.test_id)
    print block['Rule']['Interval'], self.test_rule['Interval']
    assert block['Rule']['Interval'] != self.test_rule['Interval']

    
  def teardown(self):
    st.delete_block(self.test_id)

   