# -*- coding: utf-8 -*- 
from utils import ProcessamentoTexto
from utils import PredictsModels
from utils import FileHandler
from flask import Flask, render_template, request, jsonify, session, url_for, redirect, send_from_directory
import sqlite3
import sys
from dbhandler import UserHandler
from dbhandler import RegistroHandler
from static.py.variables import sample_classes
from static.py.variables import dic_num_to_prettyclass
from static.py.variables import dic_prettyclass_to_num
import xlsxwriter

userhandler = UserHandler()
registrohandler = RegistroHandler()

app = Flask(__name__)

app.config['SESSION_PERMANENT']=False
app.config['SESSION_TYPE']='filesystem'
app.secret_key = '\xfa\x06\xeb\xaa\xadn\xee\x82\xdbWX\x15\xd4Yt!\xcf\xb4l\xa2b\x03\xf9\xad'

@app.route('/', methods=["GET","POST"])
def home():
    session["email"]=None
    if request.method == "POST":
        if request.form.get('tela')=='tutorial':
            return redirect(url_for(request.form.get('tela')))

        email_informado = str(request.form.get('email'))
        if not email_informado or '@' not in email_informado:
            return render_template('home.html')
        else:
            user = userhandler.return_user(email_informado)
            if not user:
                userhandler.add_user(email_informado)

            session["email"]=email_informado
            return redirect(url_for(request.form.get('tela')))

    return render_template('home.html')

@app.route('/texto', methods=["GET","POST"])
def texto():
    if not session.get('email'):
        return render_template("home.html")
    else:
        if request.method == "POST":
            return render_template("texto.html", text = sample_classes[request.form.get('classe')])

    return render_template("texto.html", text = "")

@app.route('/audio', methods=["GET","POST"])
def audio():
    if not session.get('email'):
        return render_template("home.html")
    elif request.method == "POST":
        filehandler = FileHandler(session["email"])
        msg = filehandler.validateAudioFile(request.files['file'])
        if msg == "":
            transcricao = filehandler.transcriptAudioFile(request.files['file'])
            return render_template("texto.html", text=transcricao)
        else:
            return render_template("audio.html", msg=msg)

    else:
        return render_template("audio.html", msg="")


@app.route('/classificacoes', methods=["GET","POST"])
def classificacoes():
    if not session.get('email'):
        return render_template("home.html")
    else:
        if request.form.get('tela') == "salvar":
            registrohandler.add_registro(
                        session.get('email'),
                        str(request.form.get('textooriginal')),
                        str(request.form.get('textoprocessado')),
                        str(request.form.get('classeinformada')),
                        dic_prettyclass_to_num[request.form.get('classecomplementnb')],
                        dic_prettyclass_to_num[request.form.get('classelinearsvc')],
                        dic_prettyclass_to_num[request.form.get('classsgdclassifier')],
                        dic_prettyclass_to_num[request.form.get('classekneighborsclassifier')],
                        dic_prettyclass_to_num[request.form.get('classemlpclassifier')],
                        dic_prettyclass_to_num[request.form.get('classerandomforestclassifier')]
                        )

        registros = registrohandler.return_registros(session.get('email'))
        return render_template('classificacoes.html', registros=registros, dic_num_to_prettyclass=dic_num_to_prettyclass)




@app.route('/classificacao', methods=["GET","POST"])
def classificacao():
    if not session.get('email'):
        return render_template("home.html")
    else:
        processamentotexto=ProcessamentoTexto()
        texto_original=str(request.form.get('textoinput'))
        texto_tratado=processamentotexto.processaTexto(texto_original)
        if texto_tratado:
            predictsmodels=PredictsModels()
            classificacoes_modelos=predictsmodels.getPredicts(texto_tratado)

            return render_template('classificacao.html',
                                    texto_original = texto_original,
                                    texto_tratado = texto_tratado,
                                    predict_ComplementNB = dic_num_to_prettyclass[classificacoes_modelos['ComplementNB']],
                                    predict_LinearSVC = dic_num_to_prettyclass[classificacoes_modelos['LinearSVC']],
                                    predict_SGDClassifier = dic_num_to_prettyclass[classificacoes_modelos['SGDClassifier']],
                                    predict_KNeighborsClassifier = dic_num_to_prettyclass[classificacoes_modelos['KNeighborsClassifier']],
                                    predict_MLPClassifier = dic_num_to_prettyclass[classificacoes_modelos['MLPClassifier']],
                                    predict_RandomForestClassifier = dic_num_to_prettyclass[classificacoes_modelos['RandomForestClassifier']])
        else:
            return render_template("texto.html", text='', msg='Algo deu errado, por favor, tente novamente.')

@app.route('/sobre')
def sobre():
    return render_template("sobre.html")

@app.route('/tutorial')
def tutorial():
    return render_template("tutorial.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/download')
def download():
    registros = registrohandler.return_registros(session.get('email'))
    workbook = xlsxwriter.Workbook('static/files/classificacoes.xlsx')
    worksheet = workbook.add_worksheet()
    row = 1
    worksheet.write(0, 0, "Id")
    worksheet.write(0, 1, "Data Hora")
    worksheet.write(0, 2, "Amostra Original")
    worksheet.write(0, 3, "Amostra Tratada")
    worksheet.write(0, 4, "Categoria Informada")
    worksheet.write(0, 5, "Categoria ComplementNB")
    worksheet.write(0, 6, "Categoria LinearSVC")
    worksheet.write(0, 7, "Categoria SGDClassifier")
    worksheet.write(0, 8, "Categoria KNeighborsClassifier")
    worksheet.write(0, 9, "Categoria MLPClassifier")
    worksheet.write(0, 10, "Categoria RandomForestClassifier")
    for registro in registros :
        worksheet.write(row, 0, registro[0])
        worksheet.write(row, 1, registro[2])
        worksheet.write(row, 2, registro[3])
        worksheet.write(row, 3, registro[4])
        worksheet.write(row, 4, dic_num_to_prettyclass[registro[5]])
        worksheet.write(row, 5, dic_num_to_prettyclass[registro[6]])
        worksheet.write(row, 6, dic_num_to_prettyclass[registro[7]])
        worksheet.write(row, 7, dic_num_to_prettyclass[registro[8]])
        worksheet.write(row, 8, dic_num_to_prettyclass[registro[9]])
        worksheet.write(row, 9, dic_num_to_prettyclass[registro[10]])
        worksheet.write(row, 10, dic_num_to_prettyclass[registro[11]])
        row += 1

    workbook.close()
    return send_from_directory('static/files/', 'classificacoes.xlsx')

if __name__ == '__main__':
    app.run(debug=True)