# server.py
#
# Base server with MongoDB, memcache,  and authenticated login
import os, glob, sys, json, time
from functools import wraps
from os import environ as env
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import pandas as pd
import numpy as np
import memcache

from flask import Flask, jsonify, redirect, request, render_template, session, url_for, flash, Response
from werkzeug.security import generate_password_hash, check_password_hash
from six.moves.urllib.parse import urlencode
from urllib.request import urlopen

# Load environment variables
try:
    load_dotenv(find_dotenv())
except:
    print('.env not found.')
    raise RuntimeError(os.getcwd())
SECRET_KEY = env.get('SECRET_KEY')
SITEBASE_URL = env.get('SITEBASE_URL')
DBNAME = env.get('DBNAME')

# Create the Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.debug = False

# MongoDB and forms
import database as db
import forms as forms
app.config['MONGODB_SETTINGS'] = {'db': DBNAME}
db.eng.init_app(app)

# Initialize memCache
memCache = memcache.Client(['127.0.0.1:11211'], debug=0)

# Handle errors
@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    return response

# Turns off caching
@app.after_request
def add_header(response):
    response.cache_control.public = True
    response.cache_control.max_age = 0
    response.cache_control.must_revalidate = True
    response.cache_control.no_cache = True
    return response

# Decorator for routes that require authentication,
# but not permissions. Stores the request path with 
# the session variable to redirect the user on callback.
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'User' not in session:
            session['requestpath'] = request.path
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

# Decorator for routes that require authorization for
# a specific role.
def requires_perm(requiredRole):
    def permission(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'User' not in session:
                session['requestpath'] = request.path
                return redirect('/login')
            user = session['User']
            roles = user['roles']
            if requiredRole not in roles:
                session['requestpath'] = request.path
                return redirect('/nopermission')
            return f(*args, **kwargs)
        return decorated
    return permission

# Landing page for users that authenticate but have no permission
@app.route('/nopermission')
@requires_auth
def nopermission():
    reqpath = SITEBASE_URL + session['requestpath']
    return render_template('nopermission.html',reqpath=reqpath)

# Login route
@app.route('/login', methods=['GET','POST'])
def login():
    # If the user didn't previously request a page, redirect to root
    if 'requestpath' not in session:
        session['requestpath'] = '/'

    form = forms.LoginForm()
    if request.method == 'POST' and form.validate():
        existing_user = db.User.objects(username=form.username.data).first()
        hashpass = generate_password_hash(form.password.data, method='sha256')
        if existing_user is None:
            form.username.errors.append('User not found.')
        elif check_password_hash(existing_user.passwordhash, form.password.data): 
            session['User'] = existing_user
            return redirect(session['requestpath'])
        else:
            form.password.errors.append('Incorrect password.')
    
    return render_template('login.html', form=form)

# Register route
@app.route('/register', methods=['GET','POST'])
def register():
    form = forms.RegistrationForm()
    if request.method == 'POST' and form.validate():
        existing_user = db.User.objects(username=form.username.data).first()
        if existing_user is None:
            # If it's the first user, assign them to the admin role
            isFirstUser = (len(db.User.objects()) == 0)
            if isFirstUser:
                roles = ['admin']
            else:
                roles = []
            # Create the new user, stored with hashed passwords
            hashpass = generate_password_hash(form.password.data, method='sha256')
            newUser = db.User(username=form.username.data,
                           firstname=form.firstname.data,
                           lastname=form.lastname.data,
                           email=form.email.data,
                           passwordhash=hashpass,
                           roles=roles)
            newUser.save()
            return redirect('/login')
        else:
            form.username.errors.append('User already exists')
    return render_template('register.html', form=form)

# Route for viewing and editing user roles.
@app.route('/roles', methods=['GET','POST'])
@requires_perm('admin')
def roles():
    form = forms.RoleForm()
    if request.method == 'POST' and form.validate():
        existing_user = db.User.objects(username=form.username.data).first()
        if existing_user is None:
            form.username.errors.append('User does not exist.')
        else:
            existingRoles = existing_user.roles
            addRole = form.addrole.data
            remRole = form.remrole.data
            if len(addRole) > 0:
                existing_user.update(roles=existingRoles.append(addRole))
                existing_user.save()
                flash('Added: ' + addRole + ' for: ' + existing_user.username)
            if len(remRole) > 0:
                if remRole in existingRoles:
                    existing_user.update(roles=existingRoles.remove(remRole))
                    existing_user.save()
                    flash('Removed: ' + remRole + ' for: ' + existing_user.username)
                else:
                    form.remrole.errors.append('Role does not exist for this user.')
    roledata = [[user.username, user.roles] for user in db.User.objects()]
    return render_template('roles.html',form=form, roledata=roledata)

# Route for logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Allows templates to call render_footer()
# Remember to filter render_footer()|safe to prevent HTML escaping
def render_footer():
    if 'User' in session:
        user = session['User']
    else:
        user = dict()
        user['firstname'] = 'Not logged in'
        user['lastname'] = ''
    return render_template('footer.html', user=user)
app.jinja_env.globals['render_footer'] = render_footer

#
# 
# Main site content:
#
#

# Home route
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/pagepublic')
def pagepublic():
    return render_template('pagepublic.html')

@app.route('/pageauthonly')
@requires_auth
def pageauthonly():
    return render_template('pageauthonly.html')

@app.route('/pageadminonly')
@requires_perm('admin')
def pageadminonly():
    return render_template('pageadminonly.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
