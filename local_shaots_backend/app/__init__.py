from flask import Flask
from flask_cors import CORS
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_mail import Mail

db = SQLAlchemy()
bcrypt = Bcrypt()
ma = Marshmallow()
mail = Mail() 

environments = {"LOCAL": "local", "STAGING": "staging", "PROD": "production"}
class App(Flask):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)

def boot_app(config_class=Config):
    app = App(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    CORS(app)
    print("booting app")

    @app.before_request
    def before_req():
        print("before request")

    from app.users.routes import users
    from app.affilates.routes import affilates
    from app.customers.routes import customers
    from app.leads.routes import leads
    

    app.register_blueprint(users)
    app.register_blueprint(affilates)
    app.register_blueprint(customers)
    app.register_blueprint(leads)
    

    return app
