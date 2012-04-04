# -*- coding: utf-8 -*-
import ConfigParser as configparser

conf = configparser.SafeConfigParser()
conf.read('stegosip.conf')
debug = int(conf.get("global", "debug"))
