from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import serial


#Função que lê o Status do Serial envaido pelo Arduino
def serial_read():
    print('Reading from Arduino over Serial. . .')
    return led_status

#Função que lê envia um comando de status pro Arduino, LED ON/OFF "0" or "1"
def serial_write(data=None):
    print("Diga qual a porta a ser usada:")
    portaserial=input()
    # Abrindo a porta Serial Arduino
    s = serial.Serial(portaserial,9600)
    print('Escrevendo {} para o Arduino pela Porta Serial '.format(data))
    s.write(data.encode())


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'
db = SQLAlchemy(app)

class Aparelhos(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    content = db.Column(db.String(200),nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self):
        return '<Aparelho %r>' %self.id

db.create_all()

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method =='POST':
        nome_disp = request.form['content']
        novo_disp = Aparelhos(content=nome_disp)

        try:
            db.session.add(novo_disp)
            db.session.commit()
            return redirect('/')
        except:
            return 'Houve um erro ao adicionar um novo Dispositivo'

    else:
        disps = Aparelhos.query.order_by(Aparelhos.date_created).all()
        return render_template('index.html', disps = disps)

@app.route('/deletar/<int:id>')
def delete(id):
    disp_to_delete = Aparelhos.query.get_or_404(id)

    try:
        db.session.delete(disp_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'Houve um problema ao excluir o dispositivo'

@app.route('/renomear/<int:id>',methods=['GET','POST'])
def update(id):
    aprl = Aparelhos.query.get_or_404(id)

    if request.method == 'POST':
        aprl.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'Houve um problema ao renomerar o dispositivo'
    else:
        return render_template('update.html', aprl = aprl)

@app.route('/controle/<int:id>',methods=['GET','POST'])
def controle(id):
    aprl = Aparelhos.query.get_or_404(id)
    if request.method == 'POST':
        #Pressionando o botão para ligar
        if request.form['on_button'] == 'Ligar':
            serial_write(data='1')
        #Pressionando o botão para desligar
        elif request.form['off_button'] == 'Desligar':
            serial_write(data='0')
            print("Desligado")
        
    elif request.method == 'GET':
        return render_template('painel_de_controle.html', aprl =aprl)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0')