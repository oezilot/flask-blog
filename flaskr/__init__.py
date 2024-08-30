# this file will contain the application factory and tells python to treat the flaskr directory to be treated as a package!

import os

from flask import Flask

# this function is the application factory function!
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True) # tells python that the instance-folder is relative to configuration files
    app.config.from_mapping( # this sets some default configuration that the app will use
        SECRET_KEY='dev', # gets overridden when deplyoing
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), # path where the database is saved
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # makes sure the instance folder where the database is stored atually exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

# authentification (used for registrstions and logins)
    from . import auth
    app.register_blueprint(auth.bp)

# bluepront for the blog
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    return app