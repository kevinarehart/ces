import webapp2, jinja2, os, re
from google.appengine.ext import db
from models import User
import hashutils

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class MainHandler(webapp2.RequestHandler):
    """ Utility class for gathering various useful methods that are used by most request handlers """

    def get_posts(self, limit, offset):
        """ Get all posts ordered by creation date (descending) """
        query = Post.all().order('-created')
        return query.fetch(limit=limit, offset=offset)

    def get_posts_by_user(self, user, limit, offset):
        """
            Get all posts by a specific user, ordered by creation date (descending).
            The user parameter will be a User object.
        """

        #filter the query so that only posts by the given user
        query = Post.all().filter('author =', user)
        return query.fetch(limit=limit, offset=offset)

    def get_user_by_name(self, username):
        """ Get a user object from the db, based on their username """
        user = db.GqlQuery("SELECT * FROM User WHERE username = '%s'" % username)
        if user:
            return user.get()

    def login_user(self, user):
        """ Login a user specified by a User object user """
        user_id = user.key().id()
        self.set_secure_cookie('user_id', str(user_id))

    def logout_user(self):
        """ Logout a user specified by a User object user """
        self.set_secure_cookie('user_id', '')

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        if cookie_val:
            return hashutils.check_secure_val(cookie_val)

    def set_secure_cookie(self, name, val):
        cookie_val = hashutils.make_secure_val(val)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

    def initialize(self, *a, **kw):
        """
            A filter to restrict access to certain pages when not logged in.
            If the request path is in the global auth_paths list, then the user
            must be signed in to access the path/resource.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))

        if not self.user and self.request.path in auth_paths:
            self.redirect('/login')

class IndexHandler(MainHandler):
    def get(self):
        #list all users
        users = User.all()
        t = jinja_env.get_template("index.html")
        response = t.render(users = users)
        self.response.write(response)

class CreateAccount(MainHandler):
    def validate_username(self, username):
      USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
      if USER_RE.match(username):
          return username
      else:
          return ""

    def validate_password(self, password):
      PWD_RE = re.compile(r"^.{3,20}$")
      if PWD_RE.match(password):
          return password
      else:
          return ""

    def validate_verify(self, password, verify):
      if password == verify:
          return verify

    def validate_email(self, email):

      # allow empty email field
      if not email:
          return ""

      EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
      if EMAIL_RE.match(email):
          return email

    def get(self):
      t = jinja_env.get_template("createaccount.html")
      response = t.render(errors={})
      self.response.out.write(response)

    def post(self):
      """
          Validate submitted data, creating a new user if all fields are valid.
          If data doesn't validate, render the form again with an error.

          This code is essentially identical to the solution to the Signup portion
          of the Formation assignment. The main modification is that we are now
          able to create a new user object and store it when we have valid data.
      """

      submitted_username = self.request.get("username")
      submitted_password = self.request.get("password")
      submitted_verify = self.request.get("verify")
      submitted_email = self.request.get("email")

      username = self.validate_username(submitted_username)
      password = self.validate_password(submitted_password)
      verify = self.validate_verify(submitted_password, submitted_verify)
      email = self.validate_email(submitted_email)

      errors = {}
      existing_user = self.get_user_by_name(username)
      has_error = False

      if existing_user:
          errors['username_error'] = "A user with that username already exists"
          has_error = True
      elif (username and password and verify and (email is not None) ):

          # create new user object and store it in the database
          pw_hash = hashutils.make_pw_hash(username, password)
          user = User(username=username, pw_hash=pw_hash)
          user.put()

          # login our new user
          self.login_user(user)
      else:
          has_error = True

          if not username:
              errors['username_error'] = "That's not a valid username"

          if not password:
              errors['password_error'] = "That's not a valid password"

          if not verify:
              errors['verify_error'] = "Passwords don't match"

          if email is None:
              errors['email_error'] = "That's not a valid email"

      if has_error:
          t = jinja_env.get_template("createaccount.html")
          response = t.render(username=username, email=email, errors=errors)
          self.response.out.write(response)
      else:
          self.redirect('/')

class GoldenCircleHandler(MainHandler):
    def get(self):
        self.response.write('Render Golden Circle Template')

class ProgramsHandler(MainHandler):
    def get(self):
        self.response.write('Render Program Template')

class DiagnosticsHandler(MainHandler):
    def get(self):
        self.response.write('Render Diagnostics Template')

class ExercisesHandler(MainHandler):
    def get(self):
        self.response.write('Render Exercise Template')

class UserIndexHandler(MainHandler):
    def get(self, username):
        users = User.all()
        t = jinja_env.get_template("welcomepage.html")
        response = t.render(users = users)
        self.response.write(response)

class LoginHandler(MainHandler):
    def render_login_form(self, error=""):
        """ Render the login form with or without an error, based on parameters """
        t = jinja_env.get_template("login.html")
        response = t.render(error=error)
        self.response.out.write(response)

    def get(self):
        self.render_login_form()

    def post(self):
        submitted_username = self.request.get("username")
        submitted_password = self.request.get("password")

        # get the user from the database
        user = self.get_user_by_name(submitted_username)

        if not user:
            self.render_login_form(error="Invalid username")
        elif hashutils.valid_pw(submitted_username, submitted_password, user.pw_hash):
            self.login_user(user)
            self.redirect('/')
        else:
            self.render_login_form(error="Invalid password")

class LogoutHandler(MainHandler):
    def get(self):
        self.logout_user()
        self.redirect('/')

class LogoutIndexHandler(MainHandler):
    def get(self, username):
        users = User.all()
        t = jinja_env.get_template("logout.html")
        response = t.render(users = users)
        self.response.out.write(response)

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/createaccount', CreateAccount),
    ('/goldencircle', GoldenCircleHandler),
    ('/programs', ProgramsHandler),
    ('/diagnostics', DiagnosticsHandler),
    ('/exercises', ExercisesHandler),
    webapp2.Route('/<username:[a-zA-Z0-9_-]{3,20}>', UserIndexHandler),
    webapp2.Route('/<id:\d+>', LogoutIndexHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler)
], debug=True)

# A list of exercises that a user must be logged in to access
auth_paths = [
    '/exercises'
]
