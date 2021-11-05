import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import yfinance as yf
import datetime
import pytz
import pandas_market_calendars as mcal
from finviz.screener import Screener
from functools import cache
import talib
import numpy as np
import re
from dateutil.parser import parse


def get_stocks():
    """ Scrapes WSBDaily's pennystock page, and returns
        a list of all the stock names and the source
        that they came from.                           """

    compiler = re.compile('\d+.*\d\d:\d\d')
    stock_list = []
    name = None
    markettype = None
    table_count = 0
    table_contents = {1: "Popular Reddit Pennystocks",
                      2: "Popular RobinHood Pennystocks",
                      3: "Popular Reddit Canada Pennystocks",
                      4: "Popular Wealthsimple Pennystocks",
                      5: "Reddit Pennystock Daily Plays",
                      6: "RobbinHood Daily Plays",
                      7: "Penny Scanner #1",
                      8: "Penny Scanner #1 Canada",
                      9: "Penny Scanner #2",
                      10: "Penny Scanner #2 Canada"}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    wsb_pennny_url = "https://wsbdaily.com/penny/"
    response = requests.get(wsb_pennny_url, headers=headers).text
    soup = BeautifulSoup(response, "html.parser")

    tz_east = pytz.timezone('US/Eastern')

    for table in soup.find_all("table", class_="css-s8p85f enavj7y0"):
        table_count += 1
        for row in table.find_all("tr"):

            # uses regex to pick out date
            # Parses to date for datetime.timestamp()
            temp = compiler.search(soup.find_all(
                "div", class_="css-1hfls2k e1b8pdim22")[table_count - 1].get_text()).group()
            date = parse(temp)
            date_east = tz_east.localize(date)

            unix_east = (datetime.datetime.timestamp(date_east))

            for stock_name in row.find_all("span", class_="css-1sctek8 e1b8pdim9"):
                name = stock_name.get_text()

            for market_type in row.find_all("td", class_="css-hogeaf e1b8pdim3"):
                markettype = market_type.get_text()

                if markettype != "OTC":
                    stock_list.append([name,
                                       markettype,
                                       table_contents[table_count],
                                       unix_east])

    return(stock_list)


def call_counter(func):
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        if wrapper.calls % 100 == 0:
            time.sleep(240)
        return func(*args, **kwargs)

    wrapper.calls = 0

    return(wrapper)


def update(file_name):
    """ Uses a web scrapper to get all penny stocks off
        wsbdaily.com, filters them out by when they
        were last updated on the website and updates
        the csv file.                               """

    new_stocks = get_stocks()
    df = pd.read_csv(file_name)

    filt = df["Time_Added"] == int(new_stocks[0][3])
    result = filt.any()

    if result == True:
        return(None)

    for stock in new_stocks:

        df2 = {"Name": stock[0], "Time_Added": stock[3],
               "Source": stock[2], }
        df = df.append(df2, ignore_index=True)

    df.to_csv(file_name, index=False)


@cache
def find_purchase_date(time_discovered):
    """ Takes in the time discovered and returnes the next
        availbable market day                           """
    current_date_utc = datetime.datetime.utcnow()
    current_date_utc = current_date_utc.replace(tzinfo=pytz.utc)
    future_date = (datetime.datetime.now() + datetime.timedelta(days=10))
    stock_exhange_calendar = mcal.get_calendar("NYSE")

    utc_time_discovered = datetime.datetime.utcfromtimestamp(time_discovered)

    # Using the stock found time stamp, the calendar will show all next
    # available trading days from that stamp in UTC time
    next_availabe_market_days = stock_exhange_calendar.schedule(
        start_date=utc_time_discovered,
        end_date=future_date,
        tz="UTC")
    # gets the next available date out of the calender
    marketdate_timestamp = next_availabe_market_days.iloc[0].iloc[0]

    return(marketdate_timestamp)


@call_counter
def get_open_price(stock, market_datetime):

    current_date_utc = datetime.datetime.utcnow()
    current_date_utc = current_date_utc.replace(tzinfo=pytz.utc)

    stock_data = yf.download(stock,
                             start=market_datetime,
                             end=current_date_utc)
    try:
        open_price = stock_data.iloc[0, 0]
    except IndexError:
        return(None)

    return(open_price)


@call_counter
def get_max_percent_change(stock, market_datetime, open_price):

    current_date_utc = datetime.datetime.utcnow()
    current_date_utc = current_date_utc.replace(tzinfo=pytz.utc)
    stock_data = yf.download(stock,
                             start=market_datetime,
                             end=current_date_utc)
    high_column = stock_data["High"]
    max_price = high_column.max()
    print(stock_data)
    print(high_column)
    print(max_price)

    dif = max_price - open_price
    try:
        percent_change = (dif / open_price) * 100
    except ZeroDivisionError:
        return None

    return(percent_change)


def calculate_percent_change(open_price, close_price):

    dif = close_price - open_price
    try:
        percent_change = (dif / open_price) * 100
    except ZeroDivisionError:
        return None

    return(percent_change)


@call_counter
def get_recent_close_price(stock):

    yf_object = yf.Ticker(stock)
    stock_data = yf_object.history()
    print(stock_data.tail(1))
    print(get_recent_close_price.calls)
    last_quote = stock_data.tail(1)["Close"].iloc[0]

    return(last_quote)


def bot(csv_name):

    update(csv_name)

    csv_df = pd.read_csv(csv_name)
    csv_df.loc[:, "Purchase_Date"] = pd.to_datetime(
        csv_df["Purchase_Date"],
        infer_datetime_format=True,
        utc=True)

    #                                        #
    #  Updates the csv files Purchase Date   #
    # This is the next available market date #
    #     after the stock was Screened       #
    #

    null_price_df = csv_df[(csv_df["Open_Price"].isna())
                           & csv_df["Purchase_Date"].isna()]

    if not null_price_df.empty:
        null_price_df.loc[:, "Purchase_Date"] = null_price_df["Time_Added"].map(
            find_purchase_date)

        csv_df.update(null_price_df)
        csv_df.to_csv(csv_name, index=False)

    #                                  #
    # Updates the csv files Open Price #
    #                                  #

    new_price_df = csv_df[(csv_df["Open_Price"].isna())
                          & (csv_df["Purchase_Date"].notna())]

    tz_utc = pytz.timezone('UTC')
    date = datetime.datetime.utcnow()
    new_utc_datetime = tz_utc.localize(date)

    # The purchase date must be 10 hours or more ago, in order to
    # get stock details
    end_of_marketday_date = new_utc_datetime - datetime.timedelta(hours=10)
    new_price_df = new_price_df[new_price_df.loc[:,
                                                 "Purchase_Date"] <= end_of_marketday_date]

    new_price_df.loc[:, "Open_Price"] = list(map(get_open_price,
                                                 new_price_df.loc[:, "Name"],
                                                 new_price_df.loc[:, "Purchase_Date"]))

    csv_df.update(new_price_df)
    csv_df.to_csv(csv_name, index=False)

    #                                        #
    # Updates Stocks Percentage Change since #
    #           finviz screened it.          #
    #                                        #

    without_percentages = csv_df[csv_df.loc[:, "Open_Price"].notna()]
    if not without_percentages.empty:

        without_percentages.loc[:, "Purchase_Date"] = pd.to_datetime(
            without_percentages["Purchase_Date"], infer_datetime_format=True, utc=True)

        without_percentages.loc[:, "Last_Close"] = without_percentages["Name"].map(
            get_recent_close_price)

        without_percentages.loc[:, "Max_Percent_Change"] = list(map(get_max_percent_change,
                                                                    without_percentages["Name"],
                                                                    without_percentages["Purchase_Date"],
                                                                    without_percentages["Open_Price"]))

        without_percentages.loc[:, "Percent_Change"] = list(map(calculate_percent_change,
                                                                without_percentages["Open_Price"],
                                                                without_percentages["Last_Close"]))
        csv_df.update(without_percentages)
        csv_df.to_csv(csv_name, index=False)


bot("WSB_Tracker.csv")
