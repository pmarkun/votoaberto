from flask import Flask, abort, redirect, flash, url_for, g
import sqlite3
from itsdangerous import URLSafeSerializer, BadSignature

DATABASE = 'votoaberto.db'

app = Flask(__name__)
app.secret_key = "woof"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = app.secret_key
    return URLSafeSerializer(secret_key)

def get_activation_link(voto):
    s = get_serializer()
    payload = s.dumps(voto)
    return url_for('activate_voto', payload=payload, _external=True)

@app.route("/")
def hello():
    print get_activation_link("3")
    return "Hello World!"

@app.route('/voto/<votacao>/<parlamentar>/<voto>')
def vota(votacao, parlamentar, voto):
    resultado = {
        'votacao' : votacao,
        'parlamentar' : parlamentar,
        'voto' : voto
    }
    
    return get_activation_link(resultado)

@app.route('/voto/activate/<payload>')
def activate_voto(payload):
    s = get_serializer()
    try:
        voto = s.loads(payload)
    except BadSignature:
        abort(404)
    return redirect("/")

if __name__ == "__main__":
    app.run()
