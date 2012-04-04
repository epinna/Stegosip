# -*- coding: utf-8 -*-

import sys, os
from core.options import conf, debug

sys.path.append('python')
sys.path.append('build/python')

disspath='dissectors'


def is_incoming(direction):
    """
    Return if marker is of an incoming or outgoing packet, as set in dissector.__setDirectionMarker()
    """
    return (direction >= 100 and direction < 200)


class dissectorDict(dict):

    dissector_index = 0
    dissector_name_map = []

    def loadDissectorsInstances(self,diss,ports=[]):

        """
        Load dinamically dissectors instance from dissectors/ directory.

        Check if dissector name exists
        Check if dissector is already loaded,
          in this case call _filterPorts() to add port ranges to dissectors.
        Else, load dissector instance in self[] dictionary

        """

        if type(diss).__name__!='list':
            print 'Error loading', diss, 'not a dissector name list.'
            return

        lst=[]
        filelst=os.listdir(disspath)

        for f in diss:

            if f in self:
                print 'Error, ', diss, 'dissector already loaded with ports', self[f]._printPorts(), '.'
                continue

            if f + '.py' in filelst:
                mod = __import__(disspath + '.' + f, fromlist = ["*"])
                classes = getattr(mod,f)
                self[f]=classes(self.dissector_index,ports)
                self.dissector_index+=1
                self.dissector_name_map.append(f)


        # SOLUZIONE PER CARICARE TUTTA UNA DIR
        #lst=[]
        #for f in os.listdir(disspath):
            #if f.endswith('.py') and not f in ['dissector.py', '__init__.py']:
                #mod = __import__(disspath + '.' + f[:-3], fromlist = ["*"])
                #classes = getattr(mod,f[:-3])
                #self.dissectors[f]=classes()

    def unloadDissectorsInstances(self, diss = []):
        """
        Unload loaded dissectors.

        If called with non argument, unload all loaded dissectors.
        Else if argument is a list, download every corresponding dissector

        """

        if not diss:
            diss = self.keys()

        if type(diss).__name__!='list':
            print 'Error unloading', diss, 'not a dissector name list.'
            return
        else:
            for f in diss:
                if f in self.keys():
                    self[f].unload()
                    del self[f]
                    # Not a real delete or correspondency between number and name is loose
                    self.dissector_name_map[self.dissector_name_map.index(f)] = ''

                #else:
                    #print 'Error unloading', diss, 'doesn\'t exists.'


    def getLoadedDissectorByMarker(self, marker):

        diss = None

        if not marker:
            if debug>2: print '[ERR] Error packet with no marker.'
        elif marker>=100 and marker<200:
            fname = self.dissector_name_map[marker-100]
            if fname:
                diss = self[fname]
        elif marker>=200 and marker<300:
            fname = self.dissector_name_map[marker-200]
            if fname:
                diss = self[fname]
        else:
            print '[ERR] Invalid marker number', marker

        return diss, is_incoming(marker)

dissd = dissectorDict()
