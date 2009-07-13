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

    def test_acl(self):
        from repoze.bfg.security import Allow
        from repoze.bfg.security import Deny
        from repoze.bfg.security import Everyone
        from repoze.mailin.monitor.models import MailInMonitor
        o = MailInMonitor('x', 'y', 'z')
        self.assertEqual(o.__acl__, [
            (Allow, 'z', ('view', 'manage')),
            (Deny, Everyone, ('view', 'manage'))
            ])

    def test_no_acl(self):
        from repoze.mailin.monitor.models import MailInMonitor
        o = MailInMonitor('x', 'y')
        self.assertEqual(o.__acl__, None)

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

    def test_iter(self):
        from repoze.mailin.monitor.models import Quarantine
        from repoze.mailin.pending import PendingQueue
        pending = PendingQueue(None, ':memory:')
        def get_pending_queue():
            return pending
        pending.quarantine('xyz', 'error_msg')
        pending.quarantine('abc', 'it broke')
        q = Quarantine(None)
        q._pending_queue = get_pending_queue
        messages = list(q)
        self.assertEqual(2, len(messages))
        self.assertEqual([('xyz', 'error_msg'), ('abc', 'it broke')], messages)

class QuarantineStatusViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_ok(self):
        from repoze.bfg.testing import DummyRequest
        from repoze.mailin.monitor.views import quarantine_status_view
        context = DummyQuarantine()
        response = quarantine_status_view(context, DummyRequest())
        self.assertEquals(response.body, 'OK')

    def test_error(self):
        from repoze.bfg.testing import DummyRequest
        from repoze.mailin.monitor.views import quarantine_status_view
        context = DummyQuarantine('x', 'y')
        response = quarantine_status_view(context, DummyRequest())
        self.assertEquals(response.body, 'ERROR')

class QuarantineListViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        from repoze.bfg.testing import DummyRequest
        from repoze.bfg.testing import registerDummyRenderer
        from repoze.mailin.monitor.views import quarantine_list_view
        context = DummyQuarantine('abc', 'xyz')
        renderer = registerDummyRenderer('templates/quarantine_list.pt')
        response = quarantine_list_view(context, DummyRequest())
        self.assertEqual(renderer.messages, [
            {'message_id': 'abc',
             'error_msg': 'error in abc',
             'url': 'http://example.com/messages/abc'},
            {'message_id': 'xyz',
             'error_msg': 'error in xyz',
             'url': 'http://example.com/messages/xyz'},
            ])

from repoze.bfg.testing import DummyModel
class DummyQuarantine(DummyModel):
    def __init__(self, *message_ids):
        monitor = DummyModel()
        monitor['quarantine'] = self
        self.message_ids = message_ids

    def empty(self):
        return not self.message_ids

    def __iter__(self):
        for message_id in self.message_ids:
            yield message_id, 'error in %s' % message_id

