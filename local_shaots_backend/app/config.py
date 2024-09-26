import os
from sqlalchemy.engine.url import URL
from decouple import config
from dotenv import load_dotenv, dotenv_values
from os import getenv

load_dotenv()
env = dotenv_values(os.getcwd()+"/.env")

ENVIRONMENT = os.environ["ENVIRONMENT"]

class Config:
    # SECRET_KEY = 'your-secret-key'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    # Flask-Mail Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'info@localshouts.com'


    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ENVIRONMENT = ENVIRONMENT
    SECRET_KEY = config("JWT_SECRET", env["JWT_SECRET"]).rstrip()

    S3_ASSETS_BUCKET = env["S3_ASSETS_BUCKET"]
    S3_PREFIX = env["S3_PREFIX"]
    S3_PRIVATE_ASSETS_BUCKET = env["S3_PRIVATE_ASSETS_BUCKET"]
    ENVIRONMENT = ENVIRONMENT

    SQLALCHEMY_DATABASE_URI = URL.create(
        **{
            "drivername": "mysql+pymysql",
            "username": config("RDS_USERNAME", env["RDS_USERNAME"]).rstrip(),
            "password": config("RDS_PASSWORD", env["RDS_PASSWORD"]).rstrip(),
            "host": config("RDS_HOST", env["RDS_HOST"]).rstrip(),
            "port": config("RDS_PORT", env["RDS_PORT"]).rstrip(),
            "database": config("RDS_DATABASE", env["RDS_DATABASE"]).rstrip(),
            "query": {"charset": "utf8mb4"},
        }
    )
    
    AWS_ENVIRONMENT = "production" if ENVIRONMENT == "PROD" else "staging"