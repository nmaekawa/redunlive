# -*- coding: utf-8 -*-

"""
test_data_masseuse
----------------------------------

Tests for `data_masseuse` module.
"""

import os
os.environ['TESTING'] = 'True'

import pytest
import json
import requests
import httpretty

from redunlive.data_masseuse import map_redunlive_ca_loc
from redunlive.data_masseuse import prep_redunlive_data
from redunlive.models import CaptureAgent
from redunlive.models import CaLocation


os.environ['CA_STATS_JSON_URL'] = 'http://localhost:8989/ca_stats.json'
os.environ['CA_STATS_USER'] = 'user'
os.environ['CA_STATS_PASSWD'] = 'pwd'

data_filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), 'ca_loc_shortmap.json' )


class TestDataMasseuse( object ):

    def setup( self ):
        txt = open( data_filename, 'r' )
        self.data = txt.read()
        txt.close()


    @httpretty.activate
    def test_redunlive_ok_data( self ):

        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel3/get_params.cgi', \
                        body = "publish_type = 0" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel4/get_params.cgi', \
                        body = "publish_type = 6" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan033.dce.harvard.edu/admin/channel4/set_params.cgi', \
                        body = "", status=201 )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan017.dce.harvard.edu/admin/channel3/get_params.cgi', \
                        body = "publish_type = 6" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan017.dce.harvard.edu/admin/channel4/get_params.cgi', \
                        body = "publish_type = 6" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan089.dce.harvard.edu/admin/channel3/get_params.cgi', \
                        body = "publish_type = 0" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan089.dce.harvard.edu/admin/channel4/get_params.cgi', \
                        body = "publish_type = 0" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan088.dce.harvard.edu/admin/channel3/get_params.cgi', \
                        body = "publish_type = 0" )
        httpretty.register_uri( httpretty.GET,
                'http://fake-epiphan088.dce.harvard.edu/admin/channel4/get_params.cgi', \
                        body = "publish_type = 0" )
        httpretty.register_uri( httpretty.GET, os.environ['CA_STATS_JSON_URL'], \
                body = self.data )

        result = prep_redunlive_data()

        assert isinstance( result, dict )
        assert "all_locations" in result.keys()
        assert "all_cas" in result.keys()
        assert len( result["all_locations"] ) == 1
        assert len( result["all_cas"] ) == 4

        assert isinstance( result["all_locations"], dict )
        assert "fake_room" in result["all_locations"].keys()

        loc = result["all_locations"]["fake_room"]
        assert isinstance( loc, CaLocation )
        assert len( loc.experimental_cas ) == 2

        assert not loc.primary_ca is None
        assert loc.primary_ca.channels['live']['publish_type'] == "0"
        assert loc.active_livestream == "secondary"



