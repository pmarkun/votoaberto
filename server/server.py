from flask import Flask, abort, redirect, flash, url_for, render_template
import json
from itsdangerous import URLSafeSerializer, BadSignature

DATABASE = 'vereadores-floripa.json'

app = Flask(__name__)
app.secret_key = "woof"

#dirty version - mudar pra DB
def update_parlamentar(voto):
    arquivo = open(DATABASE, 'r')
    ps = json.loads(arquivo.read())
    arquivo.close()
    for p in ps:
        if voto['parlamentar_id'] == p['id']:
            p['votacoes'][voto['votacao_id']] = voto['voto']
            stuff = json.dumps(ps, sort_keys=True, indent=4, separators=(',', ': '))
            arquivo = open(DATABASE, 'w')
            arquivo.write(stuff)
            arquivo.close()

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

@app.route('/votacao/<votacao>')
def votacao(votacao):
    arquivo = open(DATABASE, 'r')
    ps = json.loads(arquivo.read())
    arquivo.close() 
    return render_template('votacao.html', parlamentares=ps, votacao=votacao)

@app.route('/voto/<votacao>/<parlamentar>/<voto>')
def vota(votacao, parlamentar, voto):
    resultado = {
        'votacao_id' : votacao,
        'parlamentar_id' : parlamentar,
        'voto' : voto
    }
    print get_activation_link(resultado)
    return get_activation_link(resultado)

@app.route('/voto/activate/<payload>')
def activate_voto(payload):
    s = get_serializer()
    try:
        voto = s.loads(payload)
    except BadSignature:
        abort(404)
    update_parlamentar(voto)
    return redirect("/")

if __name__ == "__main__":
    app.debug = True
    app.run()
