from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import Everyone

from repoze.mailin.maildir import MaildirStore
from repoze.mailin.pending import PendingQueue

class MailInMonitor(object):
    __name__ = None
    __parent__ = None

    def __init__(self, pending_db_path,
                 maildir_path):
        self.pending_db_path = pending_db_path
        self.maildir_path = maildir_path

    def __getitem__(self, name):
        if name == 'quarantine':
            return Quarantine(self)

        if name == 'messages':
            return Messages(self)

        raise KeyError(name)

class Quarantine(object):
    __name__ = 'quarantine'

    def __init__(self, parent):
        self.__parent__ = parent

    def empty(self):
        pending = self._pending_queue()
        empty = True
        for q in pending.iter_quarantine():
            empty = False
            break
        del pending
        return empty

    def _pending_queue(self):
        return PendingQueue('', self.__parent__.pending_db_path)

    def __iter__(self):
        pending = self._pending_queue()
        for message_id in pending.iter_quarantine():
            yield message_id, pending.get_error_message(message_id)
        del pending

class Messages(object):
    __name__ = 'messages'

    def __init__(self, parent):
        self.__parent__ = parent

    def _mail_store(self):
        return MaildirStore(self.__parent__.maildir_path)

    def __getitem__(self, message_id):
        store = self._mail_store()
        return Message(self, message_id, store[message_id])

class Message(object):
    def __init__(self, parent, message_id, message):
        self.__parent__ = parent
        self.__name__ = self.message_id = message_id
        self.message  = message

