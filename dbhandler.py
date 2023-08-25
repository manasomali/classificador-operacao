# -*- coding: utf-8 -*- 
import sqlite3
import sys
from datetime import datetime
import os
import pytz
class UserHandler():
    def return_user(self, email):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, 'dados.db')
        conection = sqlite3.connect(abs_file_path, check_same_thread=False)
        cursor = conection.cursor()
        cursor.execute("""SELECT email FROM users WHERE email=?;""",[email])
        user = cursor.fetchone()
        conection.close()
        #print("user ja existe", file=sys.stderr)
        #print(user[0], file=sys.stderr)
        return user
    
    def add_user(self, email):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, 'dados.db')
        conection = sqlite3.connect(abs_file_path, check_same_thread=False)
        cursor = conection.cursor()
        cursor.execute("""INSERT INTO users (email, criado_em) VALUES (?, ?)""", (email, datetime.now(pytz.timezone('Brazil/East')).strftime("%d/%m/%Y %H:%M:%S")))
        if cursor.lastrowid==0:
            #print("Erro ao inserir user", file=sys.stderr)
            conection.commit()
            conection.close()
            return False
        
        conection.commit()
        conection.close()
        #print("user criado", file=sys.stderr)
        return False

class RegistroHandler():
    def return_registros(self, email):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, 'dados.db')
        conection = sqlite3.connect(abs_file_path, check_same_thread=False)
        cursor = conection.cursor()
        #print('emailbuscado', file=sys.stderr)
        #print(email, file=sys.stderr)
        cursor.execute("""SELECT * FROM registros WHERE email=?;""",[email])
        registro = cursor.fetchall()
        conection.close()
        return registro
    
    def add_registro(self, email,  amostraoriginal, amostratratada, categoriainformada, categoriacomplementnb, categorialinearsvc, categoriasgdclassifier, categoriakneighborsclassifier, categoriamlpclassifier, categoriarandomforestclassifier):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, 'dados.db')
        conection = sqlite3.connect(abs_file_path, check_same_thread=False)
        cursor = conection.cursor()
        cursor.execute("""INSERT INTO registros (email, datahora, amostraoriginal, amostratratada, categoriainformada, categoriacomplementnb, categorialinearsvc, categoriasgdclassifier, categoriakneighborsclassifier, categoriamlpclassifier, categoriarandomforestclassifier) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (email, datetime.now(pytz.timezone('Brazil/East')).strftime("%d/%m/%Y %H:%M:%S"), amostraoriginal, amostratratada, categoriainformada, categoriacomplementnb, categorialinearsvc, categoriasgdclassifier, categoriakneighborsclassifier, categoriamlpclassifier, categoriarandomforestclassifier))
        if cursor.lastrowid==0:
            #print("Erro ao inserir registro", file=sys.stderr)
            conection.commit()
            conection.close()
            return False
        
        conection.commit()
        conection.close()
        #print("registro criado", file=sys.stderr)
        return False
