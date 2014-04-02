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

_user_re = [re.compile(r'(user|login): $', re.I)]
_password_re = [re.compile(r'Password: ?$')]
_linux_re = re.compile(r'\blinux\b', re.I)

class UnixShellDriver(Driver):
    def __init__(self):
        Driver.__init__(self, 'shell_unix')
        self.user_re = _user_re
        self.password_re = _password_re

        # BSN tweak to specify what platform this device is.
        self._platform = None

    def check_head_for_os(self, string):
        if 'Welcome to Ubuntu' in string:
            self._platform = 'ubuntu'
            return 89
        if _linux_re.search(string):
            self._platform = 'generic_unix'
            return 70
        if _user_re[0].search(string):
            self._platform = 'generic_unix2'
            return 20
        return 0

    # BSN tweaks - all methods below
    def platform(self):
        return self._platform

