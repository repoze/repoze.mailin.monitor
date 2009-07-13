from repoze.bfg.security import Allow
from repoze.bfg.security import Deny
from repoze.bfg.security import Everyone

from repoze.mailin.pending import PendingQueue

class MailInMonitor(object):
    __name__ = None
    __parent__ = None

    def __init__(self, pending_db_path,
                 maildir_path,
                 required_principal=None):
        self.pending_db_path = pending_db_path
        self.maildir_path = maildir_path
        self.required_principal = required_principal

    def __getitem__(self, name):
        if name == 'quarantine':
            return Quarantine(self)
        raise KeyError(name)

    @property
    def __acl__(self):
        if self.required_principal is None:
            return None

        return [
            (Allow, self.required_principal, ('view', 'manage')),
            (Deny, Everyone, ('view', 'manage'))
            ]

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
