import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from scipy import stats
from scipy.signal import argrelextrema
import ssl
from urllib import request

def Hisse_Temel_Veriler():
    url1="https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/Temel-Degerler-Ve-Oranlar.aspx#page-1"
    context = ssl._create_unverified_context()
    response = request.urlopen(url1, context=context)
    url1 = response.read()
    df = pd.read_html(url1,decimal=',', thousands='.')                         #Tüm Hisselerin Tablolarını Aktar
    df=df[6]
    Hisseler=df['Kod'].values.tolist()
    return Hisseler

def Stock_Prices(Hisse):
    Bar = 1000
    url = f"https://www.isyatirim.com.tr/_Layouts/15/IsYatirim.Website/Common/ChartData.aspx/IntradayDelay?period=120&code={Hisse}.E.BIST&last={Bar}"
    r1 = requests.get(url).json()
    data = pd.DataFrame.from_dict(r1)
    data[['Volume', 'Close']] = pd.DataFrame(data['data'].tolist(), index=data.index)
    data.drop(columns=['data'], inplace=True)
    return data

def Trend_Channel(df):
    best_period = None
    best_r_value = 0
    periods = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
    for period in periods:
        close_data = df['Close'].tail(period)
        x = np.arange(len(close_data))
        slope, intercept, r_value, _, _ = stats.linregress(x, close_data)
        if abs(r_value) > abs(best_r_value):
            best_r_value = abs(r_value)
            best_period = period

    return best_period, best_r_value

def Plot_Trendlines(Hisse,data,best_period,rval=0.85):
    plt.close()
    close_data = data['Close'].tail(best_period)
    x_best_period = np.arange(len(close_data))
    slope_best_period, intercept_best_period, r_value_best_period, _, _ = stats.linregress(x_best_period, close_data)
    trendline=slope_best_period * x_best_period + intercept_best_period
    upper_channel = (slope_best_period * x_best_period + intercept_best_period) + (trendline.std() * 1.1)
    lower_channel = (slope_best_period * x_best_period + intercept_best_period) - (trendline.std() * 1.1)

    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'], label='Kapanış Fiyatı')
    plt.plot(data.index[-best_period:], trendline, 'g-', label=f'Trend Çizgisi (R={r_value_best_period:.2f})')
    plt.fill_between(data.index[-best_period:], upper_channel, trendline, color='lightgreen', alpha=0.3, label='Üst Kanal')
    plt.fill_between(data.index[-best_period:], trendline, lower_channel, color='lightcoral', alpha=0.3, label='Alt Kanal')
    plt.title(str(Hisse)+' Kapanış Fiyatı ve Trend Çizgisi')
    plt.xlabel('Tarih Endeksi')
    plt.ylabel('Kapanış Fiyatı')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    upper_diff = upper_channel - close_data
    lower_diff = close_data - lower_channel
    last_upper_diff = upper_diff.iloc[-1]
    last_lower_diff = lower_diff.iloc[-1]
    
    if abs(r_value_best_period) > rval and (last_upper_diff < 0):
        print(str(Hisse)+' Yazdırıldı.')
        print('Trend Yukarı yönlü kırılmış.')
        print('Hesaplanan R Değeri:'+str(abs(r_value_best_period)))
        print('Hesaplanan Fark:'+str(last_upper_diff))
        plt.savefig(f'{Hisse}_Yukarı_Kırılım.png', bbox_inches='tight', dpi=200)

    if abs(r_value_best_period) > rval and (last_lower_diff < 0):
        print(str(Hisse)+' Yazdırıldı.')
        print('Trend Aşağı yönlü kırılmış')
        print('Hesaplanan R Değeri:'+str(abs(r_value_best_period)))
        print('Hesaplanan Fark:'+str(last_lower_diff))
        plt.savefig(f'{Hisse}_Aşağı_Kırılım.png', bbox_inches='tight', dpi=200)
  
    return

Hisseler=Hisse_Temel_Veriler()
for i in range(0,len(Hisseler)):
    print(Hisseler[i])
    try:
        data=Stock_Prices(Hisseler[i])
        best_period, best_r_value = Trend_Channel(data)
        Plot_Trendlines(Hisseler[i],data,best_period)
    except:
        pass


