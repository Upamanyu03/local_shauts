import os
from sqlalchemy.engine.url import URL
from decouple import config
from dotenv import load_dotenv, dotenv_values

load_dotenv()
env = dotenv_values(os.getcwd()+"/.env")

ENVIRONMENT = os.environ["ENVIRONMENT"]

class Config:
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