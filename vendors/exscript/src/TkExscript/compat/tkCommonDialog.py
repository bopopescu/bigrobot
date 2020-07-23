#
# Instant Python
# tkCommonDialog.py,v 1.2 1997/08/14 14:17:26 guido Exp
#
# base class for tk common dialogues
#
# this module provides a base class for accessing the common
# dialogues available in Tk 4.2 and newer.  use tkFileDialog,
# tkColorChooser, and tkMessageBox to access the individual
# dialogs.
#
# written by Fredrik Lundh, May 1997
#
from Tkinter import *
class Dialog:
    command  = None
    def __init__(self, main=None, **options):
        # FIXME: should this be placed on the module level instead?
        if TkVersion < 4.2:
            raise TclError, "this module requires Tk 4.2 or newer"
        self.main  = main
        self.options = options
    def _fixoptions(self):
        pass # hook
    def _fixresult(self, widget, result):
        return result # hook
    def show(self, **options):
        # update instance options
        for k, v in options.items():
            self.options[k] = v
        self._fixoptions()
        # we need a dummy widget to properly process the options
        # (at least as long as we use Tkinter 1.63)
        w = Frame(self.main)
        try:
            s = apply(w.tk.call, (self.command,) + w._options(self.options))
            s = self._fixresult(w, s)
        finally:
            try:
                # get rid of the widget
                w.destroy()
            except:
                pass
        return s
