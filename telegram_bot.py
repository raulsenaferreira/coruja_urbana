from functools import wraps
from telegram import ChatAction
from geopy.geocoders import GoogleV3
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
ConversationHandler)
from watson_conversation import WatsonConversation
import urllib3
import json
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt



#Prototipo SQL
dburl = 'postgresql://postgres:123456@localhost:5432/hackathon'

sns.set(font_scale=3)



def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func
    
    return decorator

send_typing_action = send_action(ChatAction.TYPING)

class TelegramBot(object):

    def __init__(self):
        # self.geolocator = GoogleV3("AIzaSyCZeI8Hp5aQv7rDacBxfb4DBGbmgj2yFdA")
        self.updater = Updater(token='784082052:AAF2raPeZqdY4bcRFsBOCaTJv91y2KbXbPg')
        self.watsonConversation = WatsonConversation()
        dp = self.updater.dispatcher

        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

        start_handler = CommandHandler('start', self.start)
        dp.add_handler(start_handler)
        start_handler = CommandHandler('cancel', self.start)
        dp.add_handler(start_handler)
        echo_handler = MessageHandler(Filters.text, self.msg_handle)
        dp.add_handler(echo_handler)
        location_handler = MessageHandler(Filters.location, self.location, edited_updates=True)
        dp.add_handler(location_handler)

        # log all errors
        dp.add_error_handler(self.error)

        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        self.updater.idle()

    def cancel(self, bot, update):
        user = update.message.from_user
        update.message.reply_text('Tchau! Espero que tenha lhe ajudado.',
                                    reply_markup=ReplyKeyboardRemove())
   
    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="Olá! Sou a Lui, em que posso te ajudar?")

    def msg_handle (self, bot, update):
        user = update.message.from_user
        user_text = update.message.text
        response = self.watsonConversation.get_watson_message(user_text)
        if response['intents'][0]['intent'] ==  'crime_bairro':
            q='''select address, count(address) from violence_data where event_data BETWEEN NOW() - INTERVAL '6 HOURS' AND NOW() group by address order by count desc LIMIT 10;'''
            df = pd.read_sql(q, con=dburl)
            update.message.reply_text(df.to_string())

        elif response['intents'][0]['intent'] ==  'ranking':
            q = '''select DISTINCT(event_data), description, address from violence_data where event_data BETWEEN NOW() - INTERVAL '3000 MINUTES' AND NOW() LIMIT 10;'''
            df = pd.read_sql(q, con=dburl)
            print(df.to_string())
            update.message.reply_text(df.to_string())
        elif response['intents'][0]['intent'] == 'tipo_crime':
            userText = str(response['input']['text'])
            bairro = userText.split(' ')[1]
            self.gen_chart_address(bairro)
            bot.send_photo(chat_id=update.message.chat_id, photo=open('chart1.jpg', 'rb'))
        elif response['intents'][0]['intent'] == 'semana':
            userText = str(response['input']['text'])
            if 'Segunda' in userText:
                self.gen_chart_day('Monday')
            elif 'Terça' in userText:
                self.gen_chart_day('Tuesday')
            elif 'Quarta' in userText:
                self.gen_chart_day('Wednesday')
            elif 'Quinta' in userText:
                self.gen_chart_day('Thursday')
            elif 'Sexta' in userText:
                self.gen_chart_day('Friday')
            elif 'Sábado' in userText:
                self.gen_chart_day('Saturday')
            elif 'Domingo' in userText:
                self.gen_chart_day('Sunday')
            bot.send_photo(chat_id=update.message.chat_id, photo=open('chart2.jpg', 'rb'))
        elif response['intents'][0]['intent'] ==  'bairro':
            substring_list = ['bangu',  'barra', 'botafogo', 'campo grande', 'centro', 'copacabana', 'ilha', 'madureira', 'tijuca', 'vila']
            userText = str(response['input']['text'])
            
            finalText = ''
            terms = userText.split(' ')
            #print(terms)
            for term in terms:
                if term.lower() in substring_list:
                    finalText = term
                    print(finalText)
            q = '''SELECT DISTINCT(event_data), address, description FROM violence_data WHERE address ilike '{}' AND event_data BETWEEN NOW() - INTERVAL '600 HOURS' AND NOW() LIMIT 10;'''.format(finalText)
        
            df = pd.read_sql(q, con=dburl)
            #print(df.to_string())
            #chamar SQL com  o termo recuperado aqui. Retorno vai pro update abaixo
            update.message.reply_text(df.to_string())
        elif response['intents'][0]['intent'] ==  'mae_dinah':
            import pdb; pdb.set_trace()
            neighboor = response['intents'][0]['intent']
            res = mae_dinah(neighboor)
            print(res)
            update.message.reply_text(res)
        else:
            update.message.reply_text(response['output']['text'][0])
        # import pdb; pdb.set_trace()
        # print(user_text)

    def location(self, bot, update):
        http = urllib3.PoolManager()
        resultado = http.request('GET','https://maps.googleapis.com/maps/api/geocode/json?latlng='+str(update.message.location.latitude)+','+str(update.message.location.longitude)+'&key=AIzaSyCZeI8Hp5aQv7rDacBxfb4DBGbmgj2yFdA')
        my_json = resultado.data.decode('utf8').replace("'", '"')
        data = json.loads(my_json)
        update.message.reply_text( data['results'][0]['formatted_address'])

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        pass
        # logger.warning('Update "%s" caused error "%s"', update, error)

    def mae_dinah(self, neighboor):
        import pickle
        res=38
        model = pickle.load( open( "model_veiculos.pickle", "rb" ) )
        return model_fit.predict(res, res)

    def gen_chart_day(self, dayofweek):
        #queries db
        dburl = 'postgresql://postgres:123456@localhost:5432/hackathon'
        q = '''
            SELECT CASE 
                        WHEN vd.shift = 'night' THEN 'Noite'
                        WHEN vd.shift = 'dawn' THEN 'Madrugada'
                        WHEN vd.shift = 'afternoon' THEN 'Tarde'
                        WHEN vd.shift = 'morning' THEN 'Manhã'
                    END AS turno,
                    tv.name AS crime,
                    COUNT(*) AS nu_crimes
            FROM violence_data AS vd
            INNER JOIN type_violence AS tv ON vd.type = tv.id
            WHERE day_of_week = '{}'
            GROUP BY 1, 2
            ORDER BY 3 DESC;
        '''.format(dayofweek)
        df = pd.read_sql(q, con=dburl)

        #generates the chart
        plt.figure(figsize=(30, 10))
        plt.title('Número de Crimes por Turno do Dia', color='black', size=30)

        plt.xlabel('Turno', color='black', size=30)
        plt.ylabel('Nº de Crimes', color='black', size=30)
        sns.barplot(x='turno', y='nu_crimes', data=df, hue='crime', dodge=False)
        # plt.legend(fontsize=30, loc='upper right')
        
        #saves the chart
        plt.savefig('C:\\Users\\Administrator2\\coruja_urbana\\chart2.jpg')

    def gen_chart_address(self, address):
        #queries db
        dburl = 'postgresql://postgres:123456@localhost:5432/hackathon'
        q = '''
            SELECT CASE 
                        WHEN vd.day_of_week = 'Sunday' THEN 'Domingo'
                        WHEN vd.day_of_week = 'Monday' THEN 'Segunda'
                        WHEN vd.day_of_week = 'Tuesday' THEN 'Terça'
                        WHEN vd.day_of_week = 'Wednesday' THEN 'Quarta'
                        WHEN vd.day_of_week = 'Thursday' THEN 'Quinta'
                        WHEN vd.day_of_week = 'Friday' THEN 'Sexta'
                        ELSE 'Sábado'
                    END AS dia_semana,
                    COUNT(*) AS nu_crimes
            FROM violence_data AS vd
            INNER JOIN type_violence AS tv ON vd.type = tv.id
            WHERE vd.address = '{}'
            GROUP BY 1
            ORDER BY 2 DESC
            LIMIT 10;
        '''.format(address)
        df = pd.read_sql(q, con=dburl)

        #generates the chart
        plt.figure(figsize=(30, 10))
        plt.title('Número de Crimes por Bairro', color='black', size=30)

        plt.xlabel('Bairro', color='black', size=30)
        plt.ylabel('Nº de Crimes', color='black', size=30)
        sns.barplot(x='dia_semana', y='nu_crimes', data=df, dodge=False)
        # plt.legend(fontsize=30, loc='upper right')
        
        #saves the chart
        plt.savefig('C:\\Users\\Administrator2\\coruja_urbana\\chart1.jpg')