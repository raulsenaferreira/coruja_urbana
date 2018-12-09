import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(font_scale=3)
def gen_chart_address(address):
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
    plt.legend(fontsize=30, loc='upper right')
    
    #saves the chart
    plt.savefig('C:\\Users\\Administrator2\\coruja_urbana\\chart1.jpg')