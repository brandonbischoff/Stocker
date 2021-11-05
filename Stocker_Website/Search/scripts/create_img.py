import mplfinance as mpf
import io
import base64
import yfinance as yf
from django.core.cache import cache

def create_stock(stock_objects):
# todo why am I doing 2 calls to the yfinance api?
# todo when no data is available, the dashboard diplays a little image icon. fix that
    data = cache.get(str(stock_objects))

    if not data:
        chart_purchase_date = yf.download(stock_objects.name, start=stock_objects.purchase_date)
        ytd_chart = yf.download(stock_objects.name, period='ytd', interval='1d')

        if ytd_chart.empty:
            return

        open_price = chart_purchase_date.iloc[0, 0]
        max_price = chart_purchase_date["High"].max()
        current_price = chart_purchase_date["Close"][-1]

        max_percent_change = ((max_price - open_price) / open_price) * 100
        current_percent_change = (
                                         (current_price - open_price) / open_price) * 100

        buf = io.BytesIO()
        mpf.plot(ytd_chart,
                 style="yahoo",
                 type='candle',
                 volume=True,
                 figratio=(30, 11),
                 figscale=1,
                 savefig=dict(fname=buf, bbox_inches="tight"))
        b64 = base64.b64encode(buf.getvalue()).decode()
        cache.set(key= str(stock_objects),
                  value= [current_price,max_percent_change,current_percent_change,b64,stock_objects],
                  timeout = 60*60) # 1 hour cache
        return (current_price, max_percent_change, current_percent_change, b64, stock_objects)
    else:
        return(data[0],data[1],data[2],data[3],data[4])