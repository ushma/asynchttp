# -*- coding: utf-8 -*-

import httplib
import errno

poll_map = {}
codes = httplib.responses
DISCONNECTED = (errno.EBADF, errno.EPIPE, 
                errno.ENOTCONN, errno.ESHUTDOWN, 
                errno.ECONNABORTED, errno.ECONNRESET)

