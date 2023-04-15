from flask import Flask
# from google.cloud.sql.connector import Connector, IPTypes
from flask_sqlalchemy import SQLAlchemy

import os

from google.cloud.sql.connector import Connector, IPTypes
from google.cloud.sql.connector import connector
import pg8000

import sqlalchemy

import config

# def connect_with_connector() : # -> sqlalchemy.engine.base.Engine
#     """
#     Initializes a connection pool for a Cloud SQL instance of Postgres.

#     Uses the Cloud SQL Python Connector package.
#     """
#     # Note: Saving credentials in environment variables is convenient, but not
#     # secure - consider a more secure solution such as
#     # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
#     # keep secrets safe.

#     # instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]  # e.g. 'project:region:instance'
#     # db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
#     db_user = config.username
#     db_pass = config.password
#     db_name = config.db_name
#     instance_connection_name = config.connection_name
#     # db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
#     # db_name = os.environ["DB_NAME"]  # e.g. 'my-database'

#     # ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC


#     # initialize Cloud SQL Python Connector object
#     connector = Connector()

#     def getconn() : # -> pg8000.dbapi.Connection
#         conn: pg8000.dbapi.Connection = connector.connect(
#             instance_connection_name,
#             "pg8000",
#             user=db_user,
#             password=db_pass,
#             db=db_name,
#             ip_type=ip_type,
#         )
#         return conn

#     # The Cloud SQL Python Connector can be used with SQLAlchemy
#     # using the 'creator' argument to 'create_engine'
#     pool = sqlalchemy.create_engine(
#         "postgresql+pg8000://",
#         creator=getconn,
#         # ...
#     )
#     return pool
# import psycopg2
db_user = config.username
db_pass = config.password
db_name = config.db_name
instance_connection_name = config.connection_name
ip_type = IPTypes.PUBLIC
def getconn():
    with Connector() as connector:
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=ip_type,
        )
        return conn
# conn = psycopg2.connect(
#             host="34.68.0.151",
#             port=5432,
#             # "pg8000",
#             user=db_user,
#             password=db_pass,
#             dbname=db_name,
# )
# cursor = conn.cursor()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+pg8000://"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "creator": getconn
}
db = SQLAlchemy(app)
# db.Model
class Users(db.Model):
    # name = db.Column(db.String(255))
    id = db.Column(db.Integer, primary_key=True)
    
    def __repr__(self):
        return '<User %r>' % self.id
with app.app_context():
    Users.query.all()
# db.create_all()
# db
# # print(db)
# # with db.connect() as conn:
#     # conn.execute("CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, name varchar(255) NOT NULL, email varchar(255) NOT NULL)")
# # print(db.execute("SELECT * FROM users").fetchall())
# @app.route('/')
# def hello_world():
    
#     return 'Hello, World!'