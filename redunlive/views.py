# -*- coding: utf-8 -*-

import os

from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask.ext.login import login_user
from flask.ext.login import login_required
from flask.ext.login import fresh_login_required

from redunlive import app
from redunlive import login_manager
from redunlive.forms import LoginForm
from redunlive.models import User
from redunlive.data_masseuse import prep_redunlive_data


# init users database
USERS = {
        'admin': User(u'admin', os.environ['REDUNLIVE_ADMIN_PASSWD'] )
        }


@login_manager.user_loader
def load_user( id ):
    return USERS.get( id )

login_manager.login_view = "login"
login_manager.refresh_view = "login"


@app.route('/')
@app.route('/index')
@login_required
def index():
    data = prep_redunlive_data()
    return render_template('location_list.html',
            title = 'All Locations',
            locations = data['all_locations'].values() )


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data in USERS.keys():
            u = USERS[ form.username.data ]
            if u.password == form.password.data:
                login_user( u, remember=form.remember_me.data )
                return redirect('/index')
        flash('Given username:password unknown')

    return render_template('login.html',
            title='log IN',
            form=form)


@app.route('/toggle/<loc_id>', methods=['POST','GET'])
@fresh_login_required
def toggle( loc_id ):
    # init location-ca list
    data = prep_redunlive_data()
    location = data['all_locations'][ loc_id ]

    if os.environ['TESTING'] == 'True':
        flash('location data dump: %s' % location.debug_print() )

    # form submitted
    if request.method == 'POST':
        # if not active_device == locations[ loc_id ].active_livestream:
        if request.form['active_device'] == 'primary':
            location.primary_ca.write_live_status( '6' )
        else:
            location.primary_ca.write_live_status( '0' )
            location.secondary_ca.write_live_status( '6' )

        # make sure we have the device status
        location.primary_ca.sync_live_status()
        location.secondary_ca.sync_live_status()

    return render_template('toggle.html',
            title='active live stream',
            location = location )



