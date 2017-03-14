# all the imports
import os
import sqlite3
from flask import Flask, request,  g, redirect, render_template, \
                    session, url_for, abort, flash, jsonify

app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
# Investigate this
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


# @app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT variable_name, type FROM variable_source ORDER BY type ASC, variable_name ASC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/variable_detail/<variable_name>')
def variable_detail(variable_name):
    sql = """SELECT
    variable_name, source, type
    FROM variable_source
    WHERE variable_name = ?"""
    db = get_db()
    cur = db.execute(sql, [variable_name])
    variable_detail = cur.fetchone()
    return render_template('variable_detail.html',
                           variable_detail=variable_detail)


@app.route('/new_variable')
def new_variable():
    return render_template('variable_detail.html')


@app.route('/update_variable', methods=['POST'])
def update_variable():
    db = get_db()
    with db:
        cur = db.execute("UPDATE variable_source SET source = ? WHERE variable_name = ?",
                         [request.form['source'], request.form['variable_name']])

    return redirect('/variable_detail/{variable_name}'.format(
        variable_name=request.form['variable_name']))


@app.route('/create_variable', methods=['POST'])
def create_variable():
    db = get_db()
    with db:
        cur = db.execute("INSERT INTO variable_source (variable_name, source, type) VALUES (?,?,?)",
                         [request.form['variable_name'], request.form['source'], "calculation"])
        cur = db.execute("""INSERT INTO variable_dependencies
                            (variable_name, dependency)
                            SELECT t1.variable_name, t2.variable_name 
                            FROM variable_source t1 
                            INNER JOIN variable_source t2 
                            ON t1.source LIKE '%'||t2.variable_name||'%' 
                            WHERE 
                            t1.variable_name = ?
                            AND t2.variable_name <> ?
                            """, [request.form['variable_name'], ] * 2)

    return redirect('/variable_detail/{variable_name}'.format(
        variable_name=request.form['variable_name']))

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/test2')
def test2():
    return render_template('test2.html')

@app.route('/get_variable_source')
def get_variable_source():
    db = get_db()
    cur = db.execute("SELECT source from variable_source WHERE variable_name = ?",
                     [request.args.get('variable_name', "", type=str)])
    return jsonify(source=cur.fetchone()['source'])


# @app.route('/test3')
# def monaco_editor():
#     # return "Hello"
#     return render_template('test3.html')


@app.route('/test3')
def test3():
    return render_template('test3.html')


if __name__ == '__main__':
    # init_db()
    app.run()