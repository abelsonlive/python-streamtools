import os
from kombu import Connection, Exchange 

STREAMTOOLS_URL = 'localhost:7070'
EXCHANGE_NAME = 'python-streamtools'
EXCHANGE_TYPE='direct'
AMPQ_URL='amqp://guest:guest@localhost:5672//'

EXCHANGE = Exchange(EXCHANGE_NAME, type=EXCHANGE_TYPE)
CONN = Connection(AMPQ_URL)