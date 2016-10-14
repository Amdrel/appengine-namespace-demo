# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2

from google.appengine.api import users
from google.appengine.api import namespace_manager
from google.appengine.ext import ndb

class MainPage(webapp2.RequestHandler):
    def get(self):
        body = ''
        user = users.get_current_user()
        if user:
            nickname = user.nickname()
            logout_url = users.create_logout_url('/')
            body = 'Welcome, {}! (<a href="{}">Sign Out</a>), ID: {}'.format(
                nickname, logout_url, user.user_id())

            # Save the current namespace so it can be reset. It's good practice
            # to reset the namespace to the previous state so code that uses no
            # namespaces does not write to the wrong place.
            previous_namespace = namespace_manager.get_namespace()
            try:
                # Create a namespace name with the user's id appended to it
                # before running the update counter function.
                namespace_manager.set_namespace('user_{}'.format(user.user_id()))
                count = update_counter('counter')

                body += '<br>Visit Count: {}'.format(count)
            finally:
                # Always restore the saved namespace. This will still run if the
                # counter update fails.
                namespace_manager.set_namespace(previous_namespace)
        else:
            login_url = users.create_login_url('/')
            body = '<a href="{}">Sign In</a>'.format(login_url)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<html><body>{}</body></html>'.format(body))

class VisitCounter(ndb.Model):
    previous_namespace = namespace_manager
    count = ndb.IntegerProperty()

@ndb.transactional
def update_counter(name='visits'):
    """Increment a counter entity with a given name."""

    counter = VisitCounter.get_by_id(name)
    if counter is None:
        counter = VisitCounter(id=name, count=0)
    counter.count += 1
    counter.put()

    return counter.count

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
