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
A driver for Mininet. This was borrowed from shell.py.
"""
import re
from Exscript.protocols.drivers.driver import Driver

_user_re     = [re.compile(r'(user|login): $', re.I)]
_password_re = [re.compile(r'Password: ?$')]
_linux_re    = re.compile(r'\blinux\b', re.I)

# This should cover Mininet system's shell and cli. E.g.,
#    mininet@t6-mininet:~$
#    mininet>
#    t6-mininet>

_mininet_re  = re.compile(r'(mininet>|mininet@.*mininet.*\$)', re.I)


class MininetDriver(Driver):
    def __init__(self):
        Driver.__init__(self, 'mininet')
        self.user_re     = _user_re
        self.password_re = _password_re

    def check_head_for_os(self, string):
        self._platform = 'mininet'
        if _mininet_re.search(string):
            return 90
        if _linux_re.search(string):
            # Value is smaller than one defined in shell.py because we want it
            # to pick up shell first.
            return 70
        if _user_re[0].search(string):
            return 20
        return 0

    # BSN tweaks - all methods below
    def platform(self):
        return self._platform
