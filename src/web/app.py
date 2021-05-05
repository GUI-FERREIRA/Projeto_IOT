from flask import Flask, render_template, url_for, request, redirect
import sys
sys.path.append('../python/')

from manager import  *


app = Flask(__name__)

manager = Manager()
pinos = None


def receiver_listener(request, obj):
    global pinos
    print("i here")
    if request == PLUGS:
        pinos = obj
        print(pinos)
        return
    pinos = []


manager.setRequestListener(receiver_listener)


@app.route('/', methods=['POST', 'GET'])
def index():
    global pinos
    conexao_arduino = manager.hasArduinoConnected()
    portas = manager.get_serial()
    # portas = ['COM1','COM2'] #usadas para teste
    if not conexao_arduino:
        return render_template('index.html', portas=portas, conexao_arduino=conexao_arduino)

    if request.method == 'POST':
        nome_disp = request.form['content']
        pin = request.form['selecionar']
        manager.registerPlug(nome_disp, pin)
        return redirect('/')

    pinos = manager.getAvailablePlug()
    return render_template('index.html', portas=portas, pins=pinos, tomadas= manager.get_tomada(),conexao_arduino=conexao_arduino)


@app.route('/arduino_connect/', methods=['GET', 'POST'])  # Conectando a uma porta
def conectar():
    porta = request.args.get('porta')
    conexao, erro = manager.arduino_conect(porta)
    if conexao == False:
        return erro
    else:
        return 'CONECTANDO...', {"Refresh": "2; url=/"}


@app.route('/deletar/', methods=['GET', 'POST'])
def delete():
    p_conect = request.args.get('p_conect')
    deletado = manager.delete_plug(p_conect)
    if deletado == True:
        return redirect('/')
    else:
        return 'Houve um erro ao deletar sua tarefa, tente novamente', {"Refresh": "2; url=/"}


@app.route('/renomear/', methods=['GET', 'POST'])
def update():
    p_conect = request.args.get('p_conect')
    if request.method == 'POST':
        n_disp = request.form['content']
        manager.registerPlug(n_disp, p_conect)
        return redirect('/')
    return render_template('update.html',porta=p_conect,aparel=manager.get_tomada())


@app.route('/controle/<int:pin>', methods=['GET', 'POST'])
def controle(pin):
    manager.inverte(pin)
    led = manager.get_tomada_by_id(pin).status
    if request.method == 'POST':
        #Pressionando o botão para ligar
        if request.form['on_button'] == 'Ligar':
            manager.inverte(pin)
    
        #Pressionando o botão para desligar
        elif request.form['off_button'] == 'Desligar':
            manager.inverte(pin)
    return render_template('index.html', tomadas = manager.get_tomada(),led = led )
   

if __name__ == "__main__":
    app.run(debug=True,host ='0.0.0.0', port='2020')
