import unittest

from zope.testing.cleanup import cleanUp

class MailInMonitorModelTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_init(self):
        from repoze.mailin.monitor.models import MailInMonitor
        o = MailInMonitor('x', 'y', 'z')
        self.assertEqual(o.pending_db_path, 'x')
        self.assertEqual(o.maildir_path, 'y')
        self.assertEqual(o.required_principal, 'z')

    def test_get_quarantine(self):
        from repoze.mailin.monitor.models import MailInMonitor
        from repoze.mailin.monitor.models import Quarantine
        o = MailInMonitor('x', 'y', 'z')
        self.failUnless(isinstance(o['quarantine'], Quarantine))

    def test_key_error(self):
        from repoze.mailin.monitor.models import MailInMonitor
        o = MailInMonitor('x', 'y', 'z')
        self.assertRaises(KeyError, o.__getitem__, 'foo')

class QuarantineModelTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_init(self):
        from repoze.mailin.monitor.models import Quarantine
        x = 'x'
        q = Quarantine(x)
        self.failUnless(q.__parent__ is x)

    def test_empty_yes(self):
        from repoze.mailin.monitor.models import MailInMonitor
        from repoze.mailin.monitor.models import Quarantine
        from repoze.mailin.pending import PendingQueue
        m = MailInMonitor(':memory:', None, None)
        q = Quarantine(m)
        self.failUnless(q.empty())

    def test_empty_no(self):
        from repoze.mailin.monitor.models import Quarantine
        from repoze.mailin.pending import PendingQueue
        pending = PendingQueue(None, ':memory:')
        def get_pending_queue():
            return pending
        pending.push('xyz')
        pending.quarantine('abc')
        q = Quarantine(None)
        q._pending_queue = get_pending_queue
        self.failIf(q.empty())

