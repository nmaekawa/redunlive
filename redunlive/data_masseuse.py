# -*- coding: utf-8 -*-

import os
import re

import json
import requests
from epipearl import Epipearl

from models import CaptureAgent
from models import CaLocation

from . import log

import utils



__all__ = ['map_redunlive_ca_loc', 'prep_redunlive_data']


def prep_redunlive_data():
    json_text = utils.pull_data( os.environ['CA_STATS_JSON_URL'],
            creds={
                'user': os.environ['CA_STATS_USER'],
                'pwd': os.environ['CA_STATS_PASSWD']
                } )
    return map_redunlive_ca_loc( json.loads( json_text ) )


def map_redunlive_ca_loc( data ):
    """
    """
    all_locations = {}
    all_cas = {}

    for ca_item in data:
        loc_id = CaLocation.clean_name( ca_item['location'] )

        # create location object if not in internal map of locations
        if loc_id not in all_locations.keys():
            all_locations[ loc_id ] = CaLocation( ca_item['location'] )
        loc = all_locations[ loc_id ]

        # check required ca_item property "address"
        if not 'address' in ca_item.keys():
            log.warning( "missing 'address' for capture agent in location(%s)" \
                    % ca_item['location'] )
            continue

        # check required ca_item property "serial_number"
        serial_number = None
        if 'ca_attributes' in ca_item.keys() and \
                'serial_number' in ca_item['ca_attributes'].keys():
            serial_number = ca_item['ca_attributes']['serial_number']
        else:
            log.warning( \
                    "missing 'serial_number' for CA(%s) in location(%s)" \
                    % ( ca_item['address'], ca_item['location'] ) )
            continue

        ca = CaptureAgent( serial_number, ca_item['address'])

        if ca_item['role'] == 'Primary':
            loc.primary_ca = ca
        elif ca_item['role'] == 'Secondary':
            loc.secondary_ca = ca
        else:
            # not too worried about 'experimental' capture agents right now
            loc.experimental_cas.append( ca )

        # find the live streaming channel
        if 'channels' in ca_item['ca_attributes'].keys():
            for chan,info in ca_item['ca_attributes']['channels'].iteritems():
                if 'Live' in info['name']:
                    if not 'LowBR' in info['name']:
                        ca.channels['live']['channel'] = chan if chan else 'not available'
                        if 'publish_type' in info.keys():
                            ca.channels['live']['publish_type'] = info['publish_type']
                    else:
                        ca.channels['lowBR']['channel'] = chan if chan else 'not available'
                        if 'publish_type' in info.keys():
                            ca.channels['lowBR']['publish_type'] = info['publish_type']

        # add ca to internal list of ca's
        all_cas[ ca.serial_number ] = ca

        # sync capture agent object with actual device
        set_epipearl_client( ca )

    # end __for ca_item in data__

    return { 'all_locations': all_locations, 'all_cas': all_cas }



def set_epipearl_client( ca ):
    ca.client = Epipearl( "http://%s" % ca.address,
            os.environ['EPIPEARL_USER'],
            os.environ['EPIPEARL_PASSWD'])
    ca.sync_live_status()



# to check what map_redunlive_ca_loc generates do
# python data_masseuse.py
if __name__ == "__main__":
    import os
    import json

    data_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), '../tests/ca_loc_shortmap.json')
    txt = open( data_filename, 'r' )
    data = json.load( txt )
    txt.close()
    result = map_redunlive_ca_loc( data )

    for x in result['all_locations'].values():
        print "------------------------------------"
        print "%s" % x.debug_print()
        print "------------------------------------"









