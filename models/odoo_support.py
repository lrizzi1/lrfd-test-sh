# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.tools.misc import pickle
import odoo
import logging
import traceback
import os
import tempfile
from os import path, replace as rename
import contextlib
import time
import glob

_logger = logging.getLogger(__name__)

_fs_transaction_suffix = ".__wz_sess"

class FilesystemSessionStoreFix(http.FilesystemSessionStore):
    def save(self, session):
        session_path = self.get_session_filename(session.sid)
        dirname = os.path.dirname(session_path)
        if not os.path.isdir(dirname):
            with contextlib.suppress(OSError):
                os.mkdir(dirname, 0o0755)
        fn = path.join(self.path, self.filename_template % session.sid)
        fd, tmp = tempfile.mkstemp(suffix=_fs_transaction_suffix, dir=self.path)
        f = os.fdopen(fd, "wb")
        _logger.debug("_______________________________________________save triggered______________________________________________________")
        err_flag = 0
        try:
            pickle.dump(dict(session), f, pickle.HIGHEST_PROTOCOL)
        finally:
            f.close()
        try:
            rename(tmp, fn)
            os.chmod(fn, self.mode)
        except (IOError, OSError):
            _logger.debug('Could not load rename from disk.', exc_info=True)
            err_flag = 1
        if err_flag:
            _logger.debug('Error saving session file %s', ''.join([line for line in traceback.format_stack()]))


    def delete(self, session):
        _logger.debug("_______________________________________________delete triggered______________________________________________________")
        err_flag = 0
        fn = self.get_session_filename(session.sid)
        try:
            os.unlink(fn)
        except OSError:
            err_flag = 1
        if err_flag:
            _logger.debug('Error deleting session file %s', ''.join([line for line in traceback.format_stack()]))

    def vacuum(self, max_lifetime=http.SESSION_LIFETIME):
        threshold = time.time() - max_lifetime
        err_flag = 0
        for fname in glob.iglob(os.path.join(http.root.session_store.path, '*', '*')):
            path = os.path.join(http.root.session_store.path, fname)
            _logger.debug("_______________________________________________vacuum triggered______________________________________________________")
            try:
                if os.path.getmtime(path) < threshold:
                    os.unlink(path)
            except OSError:
                err_flag = 1
            if err_flag:
                _logger.debug('Error vacuuming session file %s', ''.join([line for line in traceback.format_stack()]))

_logger.warning (" ============================================ FILE LOADED ======================================== thx syf")
http.root.session_store = FilesystemSessionStoreFix(odoo.tools.config.session_dir, session_class=http.Session, renew_missing=True)