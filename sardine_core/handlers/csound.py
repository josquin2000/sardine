# -*- coding: utf-8 -*-

# ctcsoundSession.py:
#
# Copyright (C) 2016 Francois Pinot
#
# This code is free software; you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this code; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#


import os
from typing import Optional
import ctcsound
from .sender import Sender
from ..utils import alias_param
#from ..logger import print


__all__ = ("csoundHandler",)


class csoundHandler(Sender, ctcsound.Csound):
    """A class for running a csound session"""

    def __init__(self, csdFileName: Optional[str] = None, nudge:  Optional[float] = 0.03):
        """Start a csound session, eventually loading a csd file"""
        Sender.__init__(self)
        ctcsound.Csound.__init__(self)
        self.pt = None
        self._nudge = nudge
        if csdFileName and os.path.exists(csdFileName):
            self.csd = csdFileName
            self.startThread()
        else:
            self.csd = None



    def startThread(self):
        if self.compile_("csoundSession", self.csd) == 0:
            self.pt = ctcsound.CsoundPerformanceThread(self.cs)
            self.pt.play()


    def resetSession(self, csdFileName=None):
        """Reset the current session, eventually loading a new csd file"""
        if csdFileName and os.path.exists(csdFileName):
            self.csd = csdFileName
        if self.csd:
            self.stopPerformance()
            self.startThread()

    def stopPerformance(self):
        """Stop the current score performance if any"""
        if self.pt:
            if self.pt.status() == 0:
                self.pt.stop()
            self.pt.join()
            self.pt = None
        self.cleanup()


    def csdFileName(self):
        """Return the loaded csd filename or None"""
        return self.csd


    def note(self, pfields, absp2mode=0):
        """Send a score note to a csound instrument"""
        return self.pt.scoreEvent(absp2mode, 'i', pfields)


    def scoreEvent(self, eventType, pfields, absp2mode=False):
        """Send a score event to csound"""
        self.pt.scoreEvent(absp2mode, eventType, pfields)

    def flushMessages(self):
        """Wait until all pending messages are actually received by the performance thread"""
        if self.pt:
            self.pt.flushMessageQueue()

    @alias_param(name="instrument", alias="ins")
    @alias_param(name="pitch", alias="n")
    @alias_param(name="params", alias="prm")
    def CSN(self, instrument=1, dur=0.6, amp=0.7, pitch=440.0, params=None):
        if params is None:
            params = []
        self.note([instrument, self._nudge, dur, amp, pitch].extend(params))
