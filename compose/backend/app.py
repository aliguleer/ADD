import psycopg2
import numpy as np
import pandas.io.sql as psql
#from distutils.command import config
from flask import Flask,jsonify
from dataclasses import dataclass



app = Flask(__name__)

@dataclass
class DbConfig:
    host: str
    port: int
    dbname: str
    username: str
    password: str

config = DbConfig(
    host="db",
    port=5432,
    dbname="postgres",
    username="postgres",
    password="pass",
)


@app.route("/")
def index() -> str:
    return "Hello, World!"

@app.route("/lastvalue")
def lastvalue() -> str:

    with psycopg2.connect(
        host=config.host, port=config.port, dbname=config.dbname, user=config.username, password=config.password
    ) as connection, connection.cursor() as cursor:

        cursor.execute(
            f"SELECT date,open,high,low,close,volume_btc,volume_usd FROM Crypto ORDER BY date desc LIMIT 1;"

        )
        date,open,high,low,close,volume_btc,volume_usd = cursor.fetchone()

        return {"Date": date,"BTC Open": open,"BTC High":high,"BTC Low":low,"BTC Close":close,
                "BTC Volume":volume_btc,"USD Volume":volume_usd}



@app.route("/getvalues/<string:datep>")
def getvalues(datep: str) -> str:
    with psycopg2.connect(
         host=config.host, port=config.port, dbname=config.dbname, user=config.username, password=config.password
    ) as connection, connection.cursor() as cursor:

        cursor.execute(
            f"SELECT date,open,high,low,close,volume_btc,volume_usd FROM Crypto WHERE date between TO_DATE({datep},'YYYY-MM-DD') and TO_DATE({datep},'YYYY-MM-DD')+1;"

        )

        all=  cursor.fetchall()

        all_rows=[{"Date": row[0],"BTC Open": row[1],"BTC High":row[2],"BTC Low":row[3],"BTC Close":row[4],
                "BTC Volume":row[5],"USD Volume":row[6]} for row in all]

        return jsonify(all_rows)

@app.route("/getavg/<int:limit>")
def getavg(limit: int) -> str:
    with psycopg2.connect(
         host=config.host, port=config.port, dbname=config.dbname, user=config.username, password=config.password
    ) as connection, connection.cursor() as cursor:

        cursor.execute(
            f"SELECT SUM(close)/COUNT(*) from (SELECT close FROM Crypto order by date desc LIMIT {limit}) A;"
        )
        avgclose =  cursor.fetchone()

        return {f"Avarage of the close value for the last {limit} values": avgclose}


@app.route("/signal")
def signal() -> str:


    BTC=getdata()

    #Calculate the MACF and signal line indicator
    #Calculate the short term exponential moving average (EMA)
    ShortEMA = BTC.close.ewm(span=12, adjust=False).mean()
    #Calculate the long term exponential moving average (EMA)
    LongEMA = BTC.close.ewm(span=26, adjust=False).mean()
    #Calculate the MACD line
    MACD = ShortEMA - LongEMA
    #Calculate the signal line
    signal = MACD.ewm(span=9, adjust=False).mean()

    BTC['MACD'] = MACD
    BTC['Signal_Line'] = signal

    a = buy_sell(BTC)

    BTC['Buy_Signal_Price'] = a[0]
    BTC['Sell_Signal_Price'] = a[1]

    dt=BTC.to_json()

    return {"ShortEMA":dt}


def buy_sell(signal):
    Buy=[]
    Sell=[]
    flag=-1

    for i in range(0,len(signal)):
        if signal['MACD'][i]>signal['Signal_Line'][i]:
            Sell.append(np.nan)
            if flag!= 1:
                Buy.append(signal['close'][i])
                flag = 1
            else:
                Buy.append(np.nan)
        elif signal['MACD'][i] < signal['Signal_Line'][i]:
            Buy.append(np.nan)
            if flag != 0:
                Sell.append(signal['close'][i])
                flag = 0
            else:
                Sell.append(np.nan)
        else:
            Buy.append(np.nan)
            Sell.append(np.nan)

    return(Buy,Sell)


def getdata()-> str:
    with psycopg2.connect(
         host=config.host, port=config.port, dbname=config.dbname, user=config.username, password=config.password
    ) as connection, connection.cursor() as cursor:

        #cursor.execute(
        #    f"SELECT date,CAST(close as DECIMAL) close FROM Crypto order by date desc LIMIT 60 ;"
        #)
        #all =  cursor.fetchall()

        #all_rows=[{"date": row[0],"close": row[1]} for row in all]

        dataframe = psql.read_sql("SELECT date,CAST(close as DECIMAL) close FROM Crypto order by date desc LIMIT 60", connection)

        return dataframe


if __name__ == '__main__':
    app.run(debug=True)
