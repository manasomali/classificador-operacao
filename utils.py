# -*- coding: utf-8 -*- 
import string
import re
import unicodedata
from static.py.lexemas_raizes import substituicoes
from static.py.variables import stop_words
import pickle
from static.py.variables import classificacoes_modelos
from static.py.variables import dic_uglyclass_to_num
import os
import shutil
import sys
from dotenv import load_dotenv
import speech_recognition as sr
from scipy.io.wavfile import read
from auditok import split
import time

class ProcessamentoTexto:
    def removePontuacao(self, text):
        clean_text = []
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        words = text.split(" ")
        for word in words:
            new_token = regex.sub(u'', word)
            if not new_token == u'':
                clean_text.append(new_token)
        return " ".join(clean_text)

    def removeAcento(self, text):
        clean_text = []
        words = text.split(" ")
        for word in words:
            nfkd = unicodedata.normalize('NFKD', word)
            palavras_sem_acento = u''.join([c for c in nfkd if not unicodedata.combining(c)])
            q = re.sub('[^a-zA-Z0-9 \\\]', ' ', palavras_sem_acento)
            clean_text.append(q.lower().strip())
        return " ".join(clean_text)

    def removePlural(self, text):
        clean_text = []
        words = text.split(" ")
        for word in words:
            last_char = word[-1]
            if last_char == 's':
                word = word[:-1]
                
            clean_text.append(word)
        return " ".join(clean_text)

    def removeInho(self, text):
        clean_text = []
        words = text.split(" ")
        for word in words:
            if len(word)>=4:
                last_char = word[-4:]
                if last_char == 'inho':
                    word = word[:-4]+'o'
                if last_char == 'inha':
                    word = word[:-4]+'a'
                    
            clean_text.append(word)
        return " ".join(clean_text)

    def removeNumeros(self, text):
        clean_text = []
        words = text.split(" ")
        for word in words:
            if not word.isdigit():
                clean_text.append(word)
        return " ".join(clean_text)

    def removePequenas(self, text):
        clean_text = []
        words = text.split(" ")
        for word in words:
            if len(word)<=2:
                if word == 'kv' or word == 'mw':
                    clean_text.append(word)
            
            else:
                clean_text.append(word)
                    
        return " ".join(clean_text)

    def corrigePalavras(self, text):
        text_new = []
        words = text.split(" ")
        for word in words:
            try:
                if substituicoes[word]:
                    text_new.append(substituicoes[word])
            except:
                text_new.append(word)
        return " ".join(text_new)

    def removeStopWords(self, text):
        text_new = []
        words = text.split(" ")
        for word in words:
            if word.lower().strip() not in stop_words:
                text_new.append(word)

        return " ".join(text_new)
        
    def testVazio(self, text):
        return "transcricaovazia" if len(text.split(" "))<2 else text

    def removeRepetidos(self, lista):
        new_lista = []
        for iten in lista:
            if iten not in new_lista:
                new_lista.append(iten)
        return new_lista

    def processaTexto(self, text):
        processamentotexto = ProcessamentoTexto()
        try:
            text_sem_pontuacao = processamentotexto.removePontuacao(text)
            text_sem_acento = processamentotexto.removeAcento(text_sem_pontuacao)
            text_sem_plural = processamentotexto.removePlural(text_sem_acento)
            text_sem_inho = processamentotexto.removeInho(text_sem_plural)
            text_sem_numero = processamentotexto.removeNumeros(text_sem_inho)
            text_sem_pequenas = processamentotexto.removePequenas(text_sem_numero)
            text_corrigido = processamentotexto.corrigePalavras(text_sem_pequenas)
            text_sem_stopwords = processamentotexto.removeStopWords(text_corrigido)
            text_sem_vazio = processamentotexto.testVazio(text_sem_stopwords)
            return text_sem_vazio
        except:
            return False

class PredictsModels:
    def getPredicts(self,texto_tratado):

        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, 'models/ComplementNB')
        with open(abs_file_path, 'rb') as ComplementNBModel:
            model = pickle.load(ComplementNBModel)
            ComplementNB_result = model.predict([texto_tratado])
            classificacoes_modelos['ComplementNB']= dic_uglyclass_to_num[ComplementNB_result[0]]

        abs_file_path = os.path.join(script_dir, 'models/LinearSVC')
        with open(abs_file_path, 'rb') as LinearSVCModel:
            model = pickle.load(LinearSVCModel)
            LinearSVC_result = model.predict([texto_tratado])
            classificacoes_modelos['LinearSVC']=dic_uglyclass_to_num[LinearSVC_result[0]]

        abs_file_path = os.path.join(script_dir, 'models/SGDClassifier')
        with open(abs_file_path, 'rb') as SGDClassifierModel:
            model = pickle.load(SGDClassifierModel)
            SGDClassifier_result = model.predict([texto_tratado])
            classificacoes_modelos['SGDClassifier']=dic_uglyclass_to_num[SGDClassifier_result[0]]

        abs_file_path = os.path.join(script_dir, 'models/KNeighborsClassifier')
        with open(abs_file_path, 'rb') as KNeighborsClassifierModel:
            model = pickle.load(KNeighborsClassifierModel)
            KNeighborsClassifier_result = model.predict([texto_tratado])
            classificacoes_modelos['KNeighborsClassifier']=dic_uglyclass_to_num[KNeighborsClassifier_result[0]]

        abs_file_path = os.path.join(script_dir, 'models/MLPClassifier')
        with open(abs_file_path, 'rb') as MLPClassifierModel:
            model = pickle.load(MLPClassifierModel)
            MLPClassifier_result = model.predict([texto_tratado])
            classificacoes_modelos['MLPClassifier']=dic_uglyclass_to_num[MLPClassifier_result[0]]

        abs_file_path = os.path.join(script_dir, 'models/RandomForestClassifier')
        with open(abs_file_path, 'rb') as RandomForestClassifierModel:
            model = pickle.load(RandomForestClassifierModel)
            RandomForestClassifier_result = model.predict([texto_tratado])
            classificacoes_modelos['RandomForestClassifier']=dic_uglyclass_to_num[RandomForestClassifier_result[0]]

        return classificacoes_modelos

class FileHandler:
    def __init__(self, email):
        self.email = email

    def validateAudioFile(self,file):
        if file:
            if '.' in file.filename:
                if file.filename.rsplit('.', 1)[1].lower() in ".wav" or file.filename.rsplit('.', 1)[1].lower() in "mp3":
                    samplerate, data = read(file)
                    duration = len(data)/samplerate
                    if duration <= 180:
                        try:
                            if data.shape[1]:
                                msg='Somente áudios com um único canal (mono).'
                        except:
                            return ''
                    else:
                        msg='Duração máxima 3 minutos'
                else:
                    msg='Somente arquivos .wav ou .mp3'
            else:
                msg='Arquivo inválido'
        else:
            msg='Sem arquivo'

        return msg

    def transcriptAudioFile(self,audiofile):
        def atoi(text):
            return int(text) if text.isdigit() else text
        def natural_keys(text):
            return [ atoi(c) for c in re.split(r'(\d+)', text) ]

        filehandler=FileHandler(self.email)
        filehandler.saveAudioFile(audiofile)
        filehandler.splitAudioFile()

        load_dotenv('.env')
        WIT_AI_KEY=os.getenv('WIT_AI_KEY')
        transcricao= []
        for path, _, files in os.walk(os.path.dirname(os.path.realpath(__file__)) + '/static/files/'+str(self.email)+'/dividido'):
            for name in sorted(files, key=natural_keys):
                print(os.path.join(path, name), file=sys.stderr)
                retorno=""
                r = sr.Recognizer()
                with sr.AudioFile(os.path.join(path, name)) as source:
                    audio = r.record(source)
                    try:
                        retorno=r.recognize_wit(audio, key=WIT_AI_KEY)
                    except sr.UnknownValueError:
                        retorno=""
                    except sr.RequestError:
                        retorno="requisition error"
                
                    while retorno=="requisition error":
                        time.sleep(61)
                        try:
                            retorno=r.recognize_wit(audio, key=WIT_AI_KEY)
                        except sr.UnknownValueError:
                            retorno=""
                        except sr.RequestError:
                            retorno="requisition error"

                transcricao.append(retorno)

        filehandler.deleteAudioFiles()
        return " ".join(transcricao).strip()
    
    def saveAudioFile(self,audiofile):
        script_dir = os.path.dirname(__file__)
        os.makedirs(os.path.join(script_dir, 'static/files/'+str(self.email)+'/original'), exist_ok=True)
        abs_file_path = os.path.join(script_dir, 'static/files/'+str(self.email)+'/original')
        audiofile.save(os.path.join(abs_file_path, "original.wav"))
    
    def splitAudioFile(self):
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, 'static/files/'+str(self.email)+'/original')
        audio_regioes = split(os.path.join(abs_file_path, "original.wav"),
            min_dur=0.2,
            max_dur=20,
            max_silence=0.3,
            energy_threshold=35
        )
        os.makedirs(os.path.join(script_dir, 'static/files/'+str(self.email)+'/dividido'), exist_ok=True)
        cont=0
        for region in audio_regioes:
            region.save(os.path.join(os.path.join(script_dir, 'static/files/'+str(self.email)+'/dividido'),str(cont)+".wav"))
            cont=cont+1
    
    def deleteAudioFiles(self):
        script_dir = os.path.dirname(__file__)
        abs_usr_path = os.path.join(script_dir, 'static/files/'+str(self.email))
        shutil.rmtree(abs_usr_path, ignore_errors=True)