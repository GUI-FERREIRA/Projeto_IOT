from flask import Flask, render_template, url_for, request, redirect
import sys
sys.path.append('../python/')
from manager import *

app = Flask(__name__)
manager = Manager()

@app.route('/', methods = ['POST', 'GET'])
def index():
    if not manager.hasArduinoConnected():
        portas = manager.get_serial()
        #portas = ['COM1','COM2']
        return render_template('index.html',portas=portas)
    # if request.method =='POST':
    #     nome_disp = request.form['content']
    #     novo_disp = Tomada(nome=nome_disp)
    # else:
    #     tomadas = manager.get_AvaliablePlug()
    #     return render_template('index.html',portas=portas, tomadas= tomadas)
    # if request.method =='POST':
    #     nome_disp = request.form['content']
    #     novo_disp = Tomada(nome=nome_disp)
    #     try:
    #         manager.registerPlug()
    #         db.session.commit()
    #         return redirect('/')
    #     except:
    #         return 'Houve um erro ao adicionar um novo Dispositivo'


@app.route('/arduino_connect/',methods=['GET','POST']) # Conectando a uma porta
def conectar():
    porta = request.args.get('porta')
    conexao,erro = manager.arduino_conect(porta)
    if conexao == False:
        return erro
    else:
        return redirect('/conectado')
     
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