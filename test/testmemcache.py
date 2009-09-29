import os
import time

from concurrence import unittest, Tasklet
from concurrence.memcache.client import MemcacheConnection, MemcacheResult, Memcache

class MemcacheTest(unittest.TestCase):
    def setUp(self):
        for i in range(4):
            os.system('/usr/bin/memcached -m 10 -p %d -u nobody -l 127.0.0.1&' % (11211 + i))

    def tearDown(self):
        os.system('killall /usr/bin/memcached')

    def testNodeBasic(self):
        
        node = MemcacheConnection()
        node.connect(('127.0.0.1', 11211))

        self.assertEquals(MemcacheResult.STORED, node.set('test1', '12345'))
        self.assertEquals(MemcacheResult.STORED, node.set('test2', '67890'))

        self.assertEquals('12345', node.get('test1'))
        self.assertEquals('67890', node.get('test2'))

        self.assertEquals(None, node.get('test3'))
        self.assertEquals({'test1': '12345', 'test2': '67890'}, node.multi_get(['test1', 'test2', 'test3']))

        #update test2
        node.set('test2', 'hello world!')

        self.assertEquals({'test1': '12345', 'test2': 'hello world!'}, node.multi_get(['test1', 'test2', 'test3']))
       
        #update to unicode type
        node.set('test2', u'C\xe9line')
        self.assertEquals(u'C\xe9line', node.get('test2'))

        #update to some other type
        node.set('test2', {'piet': 'blaat', 10: 20})
        self.assertEquals({'piet': 'blaat', 10: 20}, node.get('test2'))

        #test delete
        self.assertEquals(MemcacheResult.NOT_FOUND, node.delete('test_del1'))
        self.assertEquals(MemcacheResult.STORED, node.set('test_del1', 'hello'))
        self.assertEquals('hello', node.get('test_del1'))
        self.assertEquals(MemcacheResult.DELETED, node.delete('test_del1'))
        self.assertEquals(None, node.get('test_del1'))
 
        #test add command
        node.delete('add1')
        self.assertEquals(MemcacheResult.STORED, node.add('add1', '11111'))
        self.assertEquals(MemcacheResult.NOT_STORED, node.add('add1', '22222'))

        #test replace
        self.assertEquals(MemcacheResult.STORED, node.set('replace1', '11111'))
        self.assertEquals(MemcacheResult.STORED, node.replace('replace1', '11111'))
        self.assertEquals(MemcacheResult.STORED, node.replace('replace1', '11111'))
        self.assertEquals(MemcacheResult.DELETED, node.delete('replace1'))
        self.assertEquals(MemcacheResult.NOT_STORED, node.replace('replace1', '11111'))

        node.close()
        
    def xtestSpeed(self):

        node = MemcacheConnection()
        node.connect(('127.0.0.1', 11211))

        #Tasklet.sleep(1000)

        N = 100000
        
        start = time.time()    
        for i in range(N):
            node.set('test2', 'hello world!')
        end = time.time()
        print '#set/sec', N / (end - start)
        node.close()

    def xtestMemcache(self):
        
        mc = Memcache()
        mc.set_servers([('127.0.0.1', 11211)])

        N = 10000

        start = time.time()    
        for i in range(N):
            mc.set('test2', 'hello world!')
        end = time.time()
        print '#set/sec', N / (end - start)

    def testMemcacheMultiServer(self):
        
        mc = Memcache()
        mc.set_servers([('127.0.0.1', 11211), ('127.0.0.1', 11212), ('127.0.0.1', 11213), ('127.0.0.1', 11214)])

        N = 10

        for i in range(N):
            mc.set('test%d' % i, 'hello world %d' % i)

        for i in range(N):
            print mc.get('test%d' % i)

        for i in range(20000):
            mc.get_multi(['test%d' % i for i in range(N)])

if __name__ == '__main__':
    unittest.main(timeout = 60)
