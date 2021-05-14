"""
init.py
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 

"""initialize the database"""
db = SQLAlchemy()

def create_app():
    """This method creates app, sets configuration,
    registers bluebrints


    """
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        """user_loader callback. Used to reload the user object
         from the user id stored in session

        :param user_id: 

        """
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    return app
