'''
Created on 10/giu/2011

@author: norby
'''

from core.dissector import SessionList

class rtp_sessions(SessionList):

    def __init__(self):
        """
        RTPSessions entity.

        RTPSession contains only one RTP connection.

        """

        self.conn = None

        SessionList.__init__(self)

    def update(self,new_conn):
        """
        RTPSession update.

        """

        if not self.conn:
            self.conn = new_conn
        else:
            self.conn.updateConnState(new_conn)

    def __str__(self):
        msg=''
        if self.conn:
            msg += str(self.conn)
            msg += '\n'
        return msg