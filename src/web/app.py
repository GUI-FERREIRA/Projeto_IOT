from flask import Flask, render_template, url_for, request, redirect
import sys
sys.path.append('../python/')
from manager import *

app = Flask(__name__)
manager = Manager()

@app.route('/', methods = ['POST', 'GET'])
def index():
    conexao_arduino = manager.hasArduinoConnected()
    pins = [2,3,5,6,7,12]
    portas = manager.get_serial()
    # portas = ['COM1','COM2']
    # pins = manager.get_AvaliablePlug() retorna NoneType
    if not conexao_arduino:
        return render_template('index.html',portas=portas, conexao_arduino = conexao_arduino)
    elif request.method =='POST':
        nome_disp = request.form['content']
        pin = request.form['selecionar']
        print(pin)
        estado=0
        novo_disp = Tomada(nome_disp,pin,estado)
        usadas = manager.get_tomada()
        print(usadas)
        try:
            manager.registerPlug(nome_disp,pin)
            return redirect('/')
        except:
            return 'Houve um problema ao adicionar seu dispositivo'
    else:
        tomadas = manager.tomadas.items()
        print(tomadas)
        return render_template('index.html', portas=portas,pins = pins,tomadas= tomadas, conexao_arduino = conexao_arduino)

@app.route('/arduino_connect/',methods=['GET','POST']) # Conectando a uma porta
def conectar():
    porta = request.args.get('porta')
    conexao,erro = manager.arduino_conect(porta)
    if conexao == False:
        return erro
    else:
        return 'CONECTANDO...', {"Refresh": "2; url=/"} 


@app.route('/deletar/<int:pin>')
def delete(pin):
    manager.delete_plug(pin)
    return redirect('/')

@app.route('/renomear/<int:pin>',methods=['GET','POST'])
def update(pin):
    aparel = manager.tomada(pin) #minha lista de tomadas
    if  request.method =='POST':
        n_nome = request.form['content']
        #novo_disp = Tomada(nome_disp,pin,estado)
        usadas = manager.get_tomada()
        print(usadas)
        try:
            manager.registerPlug(n_nome,pin)
            return redirect('/')
        except:
            return 'Houve um problema ao renomear seu dispositivo'
    else:
        return render_template('index.html',aparel=aparel )

@app.route('/controle/<int:pin>',methods=['GET','POST'])
def controle(pin):
    aprl = manager.tomada.items(pin)
    if request.method == 'POST':
        #Pressionando o botão para ligar
        if request.form['on_button'] == 'Ligar':
            change_plug(pin,1)
        #Pressionando o botão para desligar
        elif request.form['off_button'] == 'Desligar':
            change_plug(pin,0)   
    elif request.method == 'GET':
        return render_template('painel_de_controle.html', aprl =aprl)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0')