from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
from helpers import *
from bson.objectid import ObjectId
import yfinance as yf
import math
from ast import literal_eval

import uuid

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb+srv://2000ad21:Pass123@stockyard.etxrl3a.mongodb.net/mydb?retryWrites=true&w=majority'
# Database location on Atlas
mongo.init_app(app)


@app.route("/")
def landing(methods=['GET']):
    if request.method == 'GET':
        if request.args.get('id') is None:
            return redirect(url_for('login'))
        else:
            public_id = request.args.get('id')
            user_collection = mongo.db.Users
            user = user_collection.find_one({'public_id': public_id})
            if user is None:
                return redirect(url_for('login'), errorMsg='User not found')
            else:
                return redirect(url_for('home', id=user['public_id']))
            

# Login page (base path will redirect here if user is not logged in)
@app.route("/login", methods=['POST', 'GET'])
def login():
    # if user info has been received in the form, try to sign them in
    if request.method == 'POST':
        user_collection = mongo.db.Users
        username = request.form.get('username')
        pw = request.form.get('password')
        user = user_collection.find_one({'username': username})

        # no user found by that name? go back to login
        if user is None:
            return render_template('/login.html', badPass = 1)
        else:
            user = user_collection.find_one({'username': username}, {'password': 1})
            password_b64 = user['password']

            # if password is good, send user to appropriate homepage
            if check_password(pw, password_b64):
                user = user_collection.find_one({'username': username}, {'public_id': 1})
                public_id = user['public_id']
                return redirect(url_for('landing', id=public_id))

            else:
                # error messsage if invalid password
                return render_template('/login.html', badPass = 1)

    else:
        # if the form has not been filled out yet, route user to the form
        return render_template('/login.html')
    
# send user to registration form
@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user_collection = mongo.db.Users
        # Table to add to
        user_name = request.form.get('username')
        email = request.form.get('email')
        name = request.form.get('name')
        pw = request.form.get('password')

        cash = 10000
        holdings = []


        hashed_pw = get_hashed_password(pw)
        user_collection.insert_one(
            {'name': name, 'email': email, 'username': user_name, 'password': hashed_pw, "public_id": str(uuid.uuid4()), "cash": cash, "holdings": holdings})
        # get name from html input form
        # add name into table
        return redirect(url_for('login'))
    else:
        return render_template('/register.html')
    
@app.route("/home/<id>", methods=['GET'])
def home(id):
    # fang = ['META', 'AMZN', 'NFLX', 'GOOG', 'TSLA', 'BNTX', 'MSFT', 'NVDA']
    popular_tickers = [
    "AAPL",   # Apple Inc.
    "AMZN",   # Amazon.com, Inc.
    "MSFT",   # Microsoft Corporation
    "GOOGL",  # Alphabet Inc. (Google)
    "META",   # Meta Platforms Inc. (Facebook)
    "TSLA",   # Tesla, Inc.
    "NVDA",   # NVIDIA Corporation
    "JPM",    # JPMorgan Chase & Co.
    "V",      # Visa Inc.
    # "MA",     # Mastercard Incorporated
    # "WMT",    # Walmart Inc.
    # "PG",     # The Procter & Gamble Company
    # "DIS",    # The Walt Disney Company
    # "NFLX",   # Netflix, Inc.
    # "INTC",   # Intel Corporation
    # "AMD",    # Advanced Micro Devices, Inc.
    # "IBM",    # International Business Machines Corporation
    # "GE",     # General Electric Company
    # "UBER",   # Uber Technologies, Inc.
    # "LYFT",   # Lyft, Inc.
    # "CSCO",   # Cisco Systems, Inc.
    # "CMCSA",  # Comcast Corporation
    # "BABA",   # Alibaba Group Holding Limited
    # "PFE",    # Pfizer Inc.
    # "VZ",     # Verizon Communications Inc.
    # "HD",     # The Home Depot, Inc.
    # "PYPL",   # PayPal Holdings, Inc.
    # "ADBE",   # Adobe Inc.
    # "CRM",    # Salesforce.com, Inc.
    # "NKE",    # NIKE, Inc.
    # "ABT",    # Abbott Laboratories
    # "MRNA",   # Moderna, Inc.
    # "COST",   # Costco Wholesale Corporation
    # "XOM",    # Exxon Mobil Corporation
    # "PEP",    # PepsiCo, Inc.
    # "KO",     # The Coca-Cola Company
    # "JNJ",    # Johnson & Johnson
    # "UNH",    # UnitedHealth Group Incorporated
    # "CVS",    # CVS Health Corporation
    # "MCD",    # McDonald's Corporation
    # "BA",     # The Boeing Company
    # "T",      # AT&T Inc.
    # "TSM",    # Taiwan Semiconductor Manufacturing Company Limited
    # "WFC",    # Wells Fargo & Company
    # "C",      # Citigroup Inc.
    # "BAC",    # Bank of America Corporation
    # "AMGN",   # Amgen Inc.
    # "XOM",    # Exxon Mobil Corporation
    # "PEP",    # PepsiCo, Inc.
    # "KO",     # The Coca-Cola Company
    # "JNJ"     # Johnson & Johnson
    ]

    tickers = [yf.Ticker(ticker) for ticker in popular_tickers]
    ticker_list = []
    info_list = []

    for t in tickers:
        info_list = []
        info_list.append(t.info['shortName'])
        info_list.append(t.info['symbol'])
        

        open = t.info['open']
        close = t.info['currentPrice']
        previousClose = t.info['previousClose']
        percentChange = round(((close - previousClose) / previousClose ) * 100, 2)
        if percentChange >= 0:
            percentChangeString = f"+{round(close - previousClose, 2)} ({percentChange}%)"
        else:
            percentChangeString = f"{round(close - previousClose, 2)} ({percentChange}%)"

        info_list.append("{:.2f}".format(close))
        info_list.append("{:.2f}".format(open))
        info_list.append(percentChangeString)
        info_list.append(previousClose)


        ticker_list.append(info_list)




    if request.method == 'GET':
        return render_template('/home.html', tickers=ticker_list, id=id)
    else:
        try:
            return redirect(url_for('home', id=id))
        except Exception as e:
            return "Error in query operation " + str(e)
        

@app.route("/stock-page/<id>/<ticker>", methods=['GET', 'POST'])
def stockPage(id, ticker):

    if request.method == 'POST':
        ticker = request.form.get('tick').upper()
        stock = yf.Ticker(ticker)

    if request.method == 'GET':
        if ticker != "stock-plot.html":
            ticker = [i for i in literal_eval(ticker)]
        else:
            print(ticker)
            return render_template('/stock-plot.html')
        stock = yf.Ticker(ticker[1])

    info_list = []
    info_list.append(stock.info['shortName'])
    info_list.append(stock.info['symbol'])
    

    open = stock.info['open']
    close = stock.info['currentPrice']
    previousClose = stock.info['previousClose']
    percentChange = round(((close - previousClose) / previousClose ) * 100, 2)
    if percentChange >= 0:
        percentChangeString = f"+{round(close - previousClose, 2)} ({percentChange}%)"
    else:
        percentChangeString = f"{round(close - previousClose, 2)} ({percentChange}%)"

    info_list.append("{:.2f}".format(close))
    info_list.append("{:.2f}".format(open))
    info_list.append(percentChangeString)
    info_list.append(previousClose)
    info_list.append("{:,}".format(stock.info['volume']))
    info_list.append("{:,}".format(stock.info['averageVolume']))
    info_list.append("$" + "{:,}".format(stock.info['marketCap']))
    info_list.append("{:.2f}".format(stock.info['dayHigh']))
    info_list.append("{:.2f}".format(stock.info['dayLow']))

    # gather stock data points for display

    data = yf.download(tickers=ticker[1], period='5d', interval='5m', rounding=True)
    fig = go.Figure()

    fig.add_trace(go.Candlestick())
    fig.add_trace(go.Candlestick(x=data.index,open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = 'market data'))
    fig.update_layout(title = f'{stock.info["shortName"]} Share Price', yaxis_title = 'Stock Price (USD)', yaxis=dict(autorange=True, fixedrange=False))
    fig.update_xaxes(
    rangeslider_visible=True,
    rangebreaks=[dict(bounds=['sat', 'mon']), dict(pattern= 'hour', bounds= [16, 9.5] )],
    rangeselector=dict(
    buttons=list([
    dict(count=15, label='15m', step="minute", stepmode="backward", ),
    dict(count=45, label='45m', step="minute", stepmode="backward"),
    dict(count=1, label='1h', step="hour", stepmode="backward"),
    dict(count=1, label='1d', step="day", stepmode="backward"),
    dict(count=3, label='3d', step="day", stepmode="backward"),
    dict(step="all")
    ])
    )
    )

    plotly.offline.plot(fig, filename='templates/stock-plot.html', auto_open=False, output_type='file')    
    # build chart for stock

    return render_template('/stockPage.html', stock=info_list, id=id)




if __name__ == '__main__':
    app.run(debug=True)