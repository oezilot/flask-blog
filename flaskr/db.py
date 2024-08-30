import sqlite3

import click
from flask import current_app, g # g is where the data is stored


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # tells the connection to return rows (allows accessing columns by name)
    return g.db


# close_db checks if a connection was created by checking if g.db was set. If the connection exists, it is closed.
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# builds a connection to the sql file and the tables saved there
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# shows success message to the user
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


# this function takes an application and does the registration
def init_app(app):
    app.teardown_appcontext(close_db) # tells flask to call that function after cleaning up after returning the response
    app.cli.add_command(init_db_command) # adds a new command called flask command