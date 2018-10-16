class identificationLogic(object):
    """
    The identificationLogic class is meant to handle all logic concerning
    the key handling for the different categories required in datacards.

     The class currently has the following properties:

        generic_nominal_key     --  generic key for nominal histograms
                                    , e.g. $PROCESS_finaldiscr_$CHANNEL
                                    (member variable: _generic_nom_key)
        generic_systematics_key         --  generic key for histograms for 
                                    systematic variations , e.g. 
                                    $PROCESS_finaldiscr_$CHANNEL_$SYSTEMATIC
                                    (member variable: _generic_syst_key)
        process_identificator   --  Identifier keyword for processes
                                    , e.g. $PROCESS
                                    (member variable: _procIden)
        channel_identificator   --  Identifier keyword for categories/channels 
                                    , e.g. $CHANNEL
                                    (member variable: _chIden)
        systematics_identificator -- Identifier keyword for systematics 
                                     , e.g. $SYSTEMATIC
                                     (member variable: _systIden)
    """
    _debug = 99
    def init_variables(self):
        """
        define member variables here
        """
        self._generic_nom_key   = "$PROCESS_finaldiscr_$CHANNEL"
        self._generic_syst_key  = "$PROCESS_finaldiscr_$CHANNEL_$SYSTEMATIC"
        self._procIden = "$PROCESS" #Identifier keyword for processes
        self._chIden   = "$CHANNEL" #Identifier keyword for categories/channels
        self._systIden = "$SYSTEMATIC"  #Identifier keyword for systematics

    def __init__(   self, generic_nominal_key = "", generic_systematics_key = "", 
                    process_id_key = "", channel_id_key = "", 
                    systematics_id_key = ""):
        """
        initialize identificationLogic.
        """
        self.init_variables()
        if not generic_nominal_key == "":
            self._generic_nom_key = generic_nominal_key
        if not generic_systematics_key == "":
            self._generic_syst_key = generic_systematics_key

    def __str__(self):
        """
        print out all member variables
        """
        s = []
        s.append("Identification logic:")
        s.append("\tChannel Identification Key: %s" % self._chIden)
        s.append("\tProcess Identification Key: %s" % self._procIden)
        s.append("\tSystematics Identification Key: %s" % self._systIden)
        s.append("\tGeneric Key for nominal histograms: %s" % self._generic_nom_key)
        s.append("\tGeneric Key for systematic histograms: %s" % self._generic_syst_key)
        print "\n".join(s)

    #define properties for member variables
    @property
    def generic_nominal_key(self):
        return self._generic_nom_key
    @generic_nominal_key.setter
    def generic_nominal_key(self, key):
        if not self._procIden in key and self._debug >= 3:
            s = "WARNING: process identification keyword '%s'" % self._procIden
            s+= " is not part of new nominal key '%s'!" % key
            print s
        if not self._chIden in key and self._debug >= 3:
            s = "WARNING: channel identification keyword '%s'" % self._chIden
            s+= " is not part of new nominal key '%s'!" % key
            print s
        self._generic_nom_key = key

    @property
    def generic_systematics_key(self):
        return self._generic_syst_key
    @generic_systematics_key.setter
    def generic_systematics_key(self, key):
        if not self._procIden in key:
            s = "WARNING: process identification keyword '%s'" % self._procIden
            s+= " is not part of new systematics key '%s'!" % key
            print s
        if not self._chIden in key:
            s = "WARNING: channel identification keyword '%s'" % self._procIden
            s+= " is not part of new systematics key '%s'!" % key
            print s
        if not self._systIden in key:
            s = "WARNING: systematics ID keyword '%s'" % self._procIden
            s+= " is not part of new systematics key '%s'!" % key
            print s
        self._generic_syst_key = key

    @property
    def process_identificator(self):
        return self._procIden
    @process_identificator.setter
    def process_identificator(self, key):
        self._procIden = key

    @property
    def channel_identificator(self):
        return self._chIden
    @channel_identificator.setter
    def channel_identificator(self, key):
        self._chIden = key

    @property
    def systematics_identificator(self):
        return self._systIden
    @systematics_identificator.setter
    def systematics_identificator(self, key):
        self._systIden = key
    
    def insert_channel(self, channel_name, base_key):
        """
        build a key from 'base_key' for a specific channel 'channel_name'.
        """
        if not base_key is None or base_key == "":
            print "unsuitable base_key!"
            return "" 
        if self._chIden in base_key:
            return base_key.replace(self._chIden, channel_name)

    def insert_process(self, process_name, base_key):
        """
        build a key from 'base_key' for a specific process 'process_name'.
        """
        if not base_key is None or base_key == "":
            print "unsuitable base_key!"
            return "" 
        if self._procIden in base_key:
            return base_key.replace(self._procIden, process_name)

    def insert_systematic(self, systematic_name, base_key):
        """
        build a key from 'base_key' for a specific systematic 'systematic_name'.
        """
        if not base_key is None or base_key == "":
            print "unsuitable base_key!"
            return "" 
        if self._systIden in base_key:
            return base_key.replace(self._systIden, systematic_name)

    def build_nominal_histo_name(   self, process_name, channel_name, 
                                    base_key = ""):
        """
        build nominal histogram name for process 'process_name' in 
        category 'channel_name'. The histogram is built based on the 
        generic nominal histogram key by default.
        """
        if base_key == "" or not isinstance(base_key, str):
            base_key = self._generic_nom_key
        key = self.insert_process(  process_name=process_name,
                                    base_key = base_key)
        key = self.insert_channel(  channel_name = channel_name, 
                                    base_key = key)
        return key

    def build_systematics_histo_name_down(   self, process_name, channel_name,
                                        systematic_name, base_key = ""):
        """
        build systematic histogram name for process 'process_name' in 
        category 'channel_name' and 'down' variation for 
        systematic 'systematic_name'. The histogram is built based on the 
        generic systematic histogram key by default.
        """
        if base_key == "" or not isinstance(base_key, str):
            base_key = self._generic_syst_key
        key = self.insert_process(  process_name=process_name,
                                    base_key = base_key)
        key = self.insert_channel(  channel_name = channel_name, 
                                    base_key = key)
        key = self.insert_systematic(   systematic_name = systematic_name, 
                                        base_key = key)
        return key+"Down"

    def build_systematics_histo_name_up(   self, process_name, channel_name,
                                        systematic_name, base_key = ""):
        """
        build systematic histogram name for process 'process_name' in 
        category 'channel_name' and 'up' variation for 
        systematic 'systematic_name'. The histogram is built based on the 
        generic systematic histogram key by default.
        """
        if base_key == "" or not isinstance(base_key, str):
            base_key = self._generic_syst_key
        key = self.insert_process(  process_name=process_name,
                                    base_key = base_key)
        key = self.insert_channel(  channel_name = channel_name, 
                                    base_key = key)
        key = self.insert_systematic(   systematic_name = systematic_name, 
                                        base_key = key)
        return key+"Up"

    def build_systematics_histo_names(   self, process_name, channel_name,
                                        systematic_name, base_key = ""):
        """
        build systematic histogram name for process 'process_name' in 
        category 'channel_name' and systematic 'systematic_name'. 
        The histogram is built based on the generic systematic histogram key 
        by default. Return list of strings with two histogram names: 
        first one is for 'up' variation
        second one is for 'down' variation
        """
        up = self.build_systematics_histo_name_up(process_name = process_name, 
                                            channel_name = channel_name, 
                                            systematic_name = systematic_name, 
                                            base_key = base_key)
        down = self.build_systematics_histo_name_down(process_name=process_name, 
                                            channel_name = channel_name, 
                                            systematic_name = systematic_name, 
                                            base_key = base_key)
        return [up, down]

    def matches_generic_nominal_key(self, tocheck, process_name, 
                                    channel_name = None):
        """
        Check whether given nominal histogram name 'tocheck' is compatible
        with the generic nominal key
        """
        temp = tocheck
        if not channel_name is None:
            if channel_name in temp:
                temp = temp.replace(channel_name, self._chIden)
        if process_name in temp:
            temp = temp.replace(process_name, self._procIden)
        if temp == self._generic_nom_key:
            return True
        return False

    def matches_generic_systematic_key( self, tocheck, process_name, 
                                        channel_name = None, 
                                        systematic_name = None):
        """
        Check whether given systematic histogram name 'tocheck' is compatible
        with the generic systematic key
        """
        temp = tocheck
        if not channel_name is None and not channel_name == "":
            if channel_name in temp and not self._chIden in temp:
                temp = temp.replace(channel_name, self._chIden)
        if process_name in temp and not process_name == "":
            if not self._procIden in temp:
                temp = temp.replace(process_name, self._procIden)
        if systematic_name in temp and not systematic_name == "":
            if not self._systIden in temp:
                temp = temp.replace(systematic_name, self._systIden)

        if temp == self._generic_syst_key:
            return True
        return False