import webapp2, jinja2, os, re
from google.appengine.ext import db
from models import User
import hashutils

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class GoldenCircleHandler(MainHandler):
    def get(self):
        self.response.write('Hello world!')

class ProgramsHandler(MainHandler):
    def get(self):
        self.response.write('Hello world!')

class DiagnosticsHandler(MainHandler):
    def get(self):
        self.response.write('Hello world!')

class ExercisesHandler(MainHandler):
    def get(self):
        self.response.write('Hello world!')

class LoginHandler(MainHandler):
    def get(self):
        self.response.write('Hello world!')

class LogoutHandler(MainHandler):
    def get(self):
        self.response.write('Hello world!')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/goldencircle', GoldenCircleHandler),
    ('/programs', ProgramsHandler),
    ('/diagnostics', DiagnosticsHandler),
    ('/exercises', ExercisesHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler)
], debug=True)
