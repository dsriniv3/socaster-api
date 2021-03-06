import hashlib, re, eve, flask
from eve.auth import BasicAuth
from flask import g, current_app as app
from datetime import datetime

class SocasterAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        # use Eve's own db driver; no additional connections/resources are used
        users = app.data.driver.db['users']
        email, name = re.match("([^\|]*)\|?([^\|]*)", username).groups() #match email|name
        user = users.find_one({'email': email})
        if user:
            g.user = user
            self.set_request_auth_value(email)
            return hashlib.md5(password).hexdigest() == user['auth_hash']
        else:
            auth_hash = hashlib.md5(password).hexdigest()
            self.set_request_auth_value(email)
            dt = datetime.now()
            g.user = {
                'name': name,
                'email': email,
                'auth_hash': auth_hash,
                'roles': ['user'],
                eve.DATE_CREATED: dt,
                eve.LAST_UPDATED: dt
            }
            g.user['_id'] = app.data.insert('users', g.user)
            return True
