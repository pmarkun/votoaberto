# -*- coding: utf-8 -*-

from flask import Flask, abort, redirect, flash, url_for, render_template
from flask_mail import Mail, Message
import json
from itsdangerous import URLSafeSerializer, BadSignature

DATABASE = 'vereadores-floripa.json'

app = Flask(__name__)
app.secret_key = "woof"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'pedro@markun.com.br'
app.config['MAIL_PASSWORD'] = 'senha'
mail = Mail(app)

#dirty version - mudar pra DB?
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
    subject = "Confirmacao do Voto Aberto - " + resultado['votacao_id']
    sender = "contato@votoaberto.org.br"
    recipients = ["pedro@markun.com.br"]
    msg = Message(subject,
        sender=sender,
        recipients=recipients)
    msg.html = render_template('confirmacao.html', voto=voto, link=get_activation_link(resultado))
    mail.send(msg)
    return "Caro Parlamentar,<br /> Você vai receber um email para confirmar seu voto."

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