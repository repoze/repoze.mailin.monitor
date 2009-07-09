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

class Quarantine(object):
    __name__ = 'quarantine'

    def __init__(self, parent):
        self.__parent__ = parent

    def empty(self):
        pending = PendingQueue('', self.__parent__.pending_db_path)
        empty = True
        for q in pending.iter_quarantine():
            empty = False
            break
        del pending
        return empty

