# Copyright (C) 2007-2010 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
A generic shell driver that handles unknown unix shells.
BSN note: This was borrowed from shell.py and customize for Big Switch Networks.
"""
import re
from Exscript.protocols.drivers.driver import Driver

_user_re = [re.compile(r'(user name) +: $', re.I)]
_password_re = [re.compile(r'Password +: ?$')]
_linux_re = re.compile(r'\blinux\b', re.I)

class ApcPduDriver(Driver):
    def __init__(self):
        Driver.__init__(self, 'apc_pdu')
        self.user_re = _user_re
        self.password_re = _password_re

        # BSN tweak to specify what platform this device is.
        self._platform = None

    def check_head_for_os(self, string):
        if 'American Power Conversion' in string:
            self._platform = 'apc_pdu'
            return 89
        return 0

    def init_terminal(self, conn):
        #if self.platform == 'ubuntu':
        #    conn.execute('export COLUMNS=200')
        pass

    # BSN tweaks - all methods below
    def platform(self):
        return self._platform

