import unittest

from pyramid.testing import cleanUp

class MailInMonitorModelTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_init(self):
        from repoze.mailin.monitor.models import MailInMonitor
        o = MailInMonitor('x', 'y')
        self.assertEqual(o.pending_db_path, 'x')
        self.assertEqual(o.maildir_path, 'y')

    def test_get_quarantine(self):
        from repoze.mailin.monitor.models import MailInMonitor
        from repoze.mailin.monitor.models import Quarantine
        o = MailInMonitor('x', 'y')
        self.failUnless(isinstance(o['quarantine'], Quarantine))

    def test_get_messages(self):
        from repoze.mailin.monitor.models import MailInMonitor
        from repoze.mailin.monitor.models import Messages
        o = MailInMonitor('x', 'y')
        self.failUnless(isinstance(o['messages'], Messages))

    def test_key_error(self):
        from repoze.mailin.monitor.models import MailInMonitor
        o = MailInMonitor('x', 'y')
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
        m = MailInMonitor(':memory:', None)
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

class MessagesModelTests(unittest.TestCase):
    _tempdir = None

    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

        if self._tempdir is not None:
            import shutil
            shutil.rmtree(self._tempdir)

    def _getTempdir(self):
        import tempfile
        if self._tempdir is None:
            self._tempdir = tempfile.mkdtemp()
        return self._tempdir

    def test_init(self):
        from repoze.mailin.monitor.models import Messages
        parent = object()
        o = Messages(parent)
        self.assertEqual('messages', o.__name__)
        self.failUnless(o.__parent__ is parent)

    def test_get_mail_store(self):
        from pyramid.testing import DummyModel
        from repoze.mailin.maildir import MaildirStore
        from repoze.mailin.monitor.models import Messages
        monitor = DummyModel()
        monitor.maildir_path = self._getTempdir()
        o = Messages(monitor)
        self.failUnless(isinstance(o._mail_store(), MaildirStore))

    def test_get_existing_message(self):
        from repoze.mailin.monitor.models import Messages
        from repoze.mailin.monitor.models import Message
        store = DummyMaildirStore(abc='message')
        def get_store():
            return store
        o = Messages(None)
        o._mail_store = get_store
        self.failUnless(isinstance(o['abc'], Message))
        self.assertEqual(str(o['abc'].message), 'message')

class QuarantineStatusViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_ok(self):
        from pyramid.testing import DummyRequest
        from repoze.mailin.monitor.views import quarantine_status_view
        context = DummyQuarantine()
        response = quarantine_status_view(context, DummyRequest())
        self.assertEquals(response.body, 'OK')

    def test_error(self):
        from pyramid.testing import DummyRequest
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
        from pyramid.testing import DummyRequest
        from pyramid.testing import registerDummyRenderer
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

class ShowMessageViewTests(unittest.TestCase):
    def setUp(self):
        cleanUp()

    def tearDown(self):
        cleanUp()

    def test_it(self):
        from pyramid.testing import DummyModel
        from pyramid.testing import DummyRequest
        from pyramid.testing import registerDummyRenderer
        context = DummyModel()
        context.message_id = 'foo'
        context.message = 'bar'
        renderer = registerDummyRenderer('templates/show_message.pt')
        from repoze.mailin.monitor.views import show_message_view
        response = show_message_view(context, DummyRequest())
        self.assertEqual(renderer.message_id, 'foo')
        self.assertEqual(renderer.raw, 'bar')

from pyramid.testing import DummyModel
class DummyQuarantine(DummyModel):
    def __init__(self, *message_ids):
        DummyModel.__init__(self)
        monitor = DummyModel()
        monitor['quarantine'] = self
        self.message_ids = message_ids

    def empty(self):
        return not self.message_ids

    def __iter__(self):
        for message_id in self.message_ids:
            yield message_id, 'error in %s' % message_id

class DummyMaildirStore(DummyModel):
    def __init__(self, **kw):
        DummyModel.__init__(self)
        for k,v in kw.items():
            self[k] = DummyMessage(v)

class DummyMessage(DummyModel):
    def __init__(self, message):
        DummyModel.__init__(self)
        self.message = message

    def __str__(self):
        return self.message
