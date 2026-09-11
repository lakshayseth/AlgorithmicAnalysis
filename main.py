from data.instrument import instrument
from data.tickers import *
from signals.core.registry import get_signal
from strategies.nnfx import NNFX 
from strategies.ichimoku import ICHIMOKU

import os
import time
import smtplib
from email.mime.text import MIMEText

import warnings
warnings.filterwarnings("ignore")

import logging
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger("tvDataFeed").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
log = []

def main(a, b, c):
    baseline = get_signal("kijunsen")()
    c1 = get_signal("ssl")()
    c2 = get_signal("absolute_strength")()
    volume = get_signal("wae")()
    atr = get_signal("atr")(period=14)
    nnfx = NNFX(
        baseline=baseline,
        c1=c1,
        c2=c2,
        volume=volume,
        atr=atr
    )
    
    ichm = get_signal("ichimoku_cloud")()
    ichimoku = ICHIMOKU(ichm, atr)    
    
    for i in range(len(a)):
        symbol = a[i]
        exchange = b[i]

        log.append(symbol)
        print(symbol)
        
        info = instrument(symbol, exchange, c)
        result = nnfx.analyze(info.data)
        if result is not None:
            log.append(f"{symbol}: NNFX: {result}")
            print(symbol, result)
            
        result2 = ichimoku.analyze(info.data)
        if result2 is not None:
            log.append(f"{symbol}: ICHIMOKU: {result2}")
            print(symbol, result2)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def send_email(log):
    content = "\n".join(log)

    msg = MIMEText(content)
    msg["Subject"] = "Daily Trading Signals"
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_USER

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully")

    except Exception as e:
        print("Email failed:", e)

def run_all(period, delay):
    log.clear()  
       
    main(forex, exchange_forex, period)
    time.sleep(delay)

    main(index, exchange_index, period)
    time.sleep(delay)

    main(metal_energy, exchange_metals_energy, period)
    time.sleep(delay)

    main(other_combined, exchange_other_combined, period)
    time.sleep(delay)

    main(grains, exchange_grains, period)
    time.sleep(delay)

    main(sectors, exchange_sectors, period)
    time.sleep(delay)

    main(crypto, exchange_crypto, period)
    
    send_email(log)

if __name__ == '__main__':
    run_all(period='D', delay=5)
