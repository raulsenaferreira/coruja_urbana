import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set(font_scale=3)
def gen_chart_day(dayofweek):
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
    plt.legend(fontsize=30, loc='upper right')
    
    #saves the chart
    plt.savefig('C:\\Users\\Administrator2\\coruja_urbana\\chart2.jpg')