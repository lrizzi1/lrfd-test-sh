# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
import logging
import traceback
import os

_logger = logging.getLogger(__name__)

class FilesystemSessionStoreFix(http.FilesystemSessionStore):
    def delete(self, session):
        _logger.debug("debug message")
        err_flag = 0
        fn = self.get_session_filename(session.sid)
        try:
            os.unlink(fn)
        except OSError:
            err_flag = 1
        if err_flag:
            _logger.debug('Error deleting session file %s', ''.join([line for line in traceback.format_stack()]))

http.FilesystemSessionStore = FilesystemSessionStoreFix