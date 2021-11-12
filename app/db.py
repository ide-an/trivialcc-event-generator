from sqlalchemy import create_engine
from sqlalchemy.orm import (
        declarative_base, scoped_session, sessionmaker
)
import click
from flask.cli import with_appcontext

engine = create_engine('sqlite:///test.db')
db_session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import app.models
    Base.metadata.create_all(engine)

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database')
