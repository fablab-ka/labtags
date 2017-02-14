import unittest
from mock import Mock

from gateway import WorkerThread
from tagcache import TagCache
from tag import Tag
from messagequeue import MessageQueue
from messages import Message

class GatewayTest(unittest.TestCase):

    def createWorker(self):
        messageQueue = Mock()
        blotClient = Mock()
        tagCache = []
        worker = WorkerThread(messageQueue, blotClient, tagCache)
        return worker

    def runTest(self):
        worker = self.createWorker()
        tagConnectionMock = Mock()
        tagConnectionMock.dead = True
        worker.tagConnections.append(tagConnectionMock)
        worker.pruneTagConnections()
        self.assertEqual(len(worker.tagConnections), 0)

class TagCacheTest(unittest.TestCase):
    def runTest(self):
        expectedMac = "testmac"
        tagCache = TagCache()
        testTag = Tag(expectedMac, None, None)
        tagCache.append(testTag)
        self.assertEqual(len(tagCache.data), 1)
        self.assertEqual(tagCache.data[0].mac, expectedMac)
        self.assertEqual(tagCache.hasTagByMac(expectedMac), True)
        self.assertEqual(tagCache.findByMac(expectedMac), testTag)

        tagCache.remove(testTag)

        self.assertEqual(len(tagCache.data), 0)
        self.assertEqual(tagCache.hasTagByMac(expectedMac), False)
        self.assertEqual(tagCache.findByMac(expectedMac), None)

class MessageQueueTest(unittest.TestCase):
    def runTest(self):
        messageQueue = MessageQueue()
        testMessage = Message()
        messageQueue.put(testMessage)

        self.assertEqual(messageQueue.empty(), False)

        actualMessage = messageQueue.get()

        self.assertEqual(actualMessage, testMessage)
        self.assertEqual(messageQueue.empty(), True)


if __name__ == '__main__':
    unittest.main()
