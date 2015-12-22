# -*- coding: utf-8 -*-

__version__='0.1.0'

import os

from flask import Flask
from flask.ext.login import LoginManager


app = Flask(__name__)
app.config.from_object('config')

if app.debug is not True and not os.environ['TESTING'] == 'True':
    import logging
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler( \
            app.config['LOG_FULLPATH'], \
            when='D', interval=1, backupCount=7 )
    formatter = logging.Formatter( "%(asctime)s:%(name)s[%(levelname)s] %(message)s" )
    file_handler.setFormatter( formatter )
    app.logger.addHandler( file_handler )
    app.logger.setLevel( app.config['LOG_LEVEL'] )

log = app.logger

login_manager = LoginManager()
login_manager.init_app( app )


from redunlive import views
from redunlive import models
from redunlive import forms
from redunlive import data_masseuse
from redunlive import utils




