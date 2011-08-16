from pyramid_zcml import make_app as bfg_make_app
from repoze.mailin.monitor.models import MailInMonitor

import repoze.mailin.monitor

def make_app(global_config,
             pending_db_path,
             maildir_path,
             required_principal,
             **options):

    def root_factory(environ):
        return MailInMonitor(pending_db_path, maildir_path, required_principal)

    return bfg_make_app(root_factory, repoze.mailin.monitor, options=options)
