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

def average_share(x, id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    holdings = user['holdings']
    stock_list = []
    for i in holdings:
        if x[0] == i[0]:
            stock_list.append([i[3], i[1]])
    total = 0
    shares = 0
    for i in stock_list:
        total += i[0]
        shares += int(i[1])
    return "{:,.2f}".format(total / shares)


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
        cash = request.form.get('startCash')

        cash = float(cash)
        startingCash = float(cash)
        holdings = []
        holdingsConsolidated = []


        hashed_pw = get_hashed_password(pw)
        user_collection.insert_one(
            {'name': name, 'email': email, 'username': user_name, 'password': hashed_pw, "public_id": str(uuid.uuid4()), "cash": cash,
              "holdings": holdings, "holdingsConsolidated" : holdingsConsolidated, 'startingCash' : startingCash})
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
        data = yf.download(ticker, period='5d', interval='5m', rounding=True)
    elif request.method == 'GET':
        if ticker != "stock-plot.html":
            ticker = [i for i in literal_eval(ticker)]
            data = yf.download(tickers=ticker[1], period='5d', interval='5m', rounding=True)
        else:
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

    # use stock data points for display candlestick
    fig = go.Figure()

    fig.add_trace(go.Candlestick())
    fig.add_trace(go.Candlestick(x=data.index,open = data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name = 'market data'))
    fig.update_layout(title = f'{stock.info["shortName"]} ({stock.ticker}) Share Price', yaxis_title = 'Stock Price (USD)', yaxis=dict(autorange=True, fixedrange=False))
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


@app.route("/buy/<id>/<ticker>", methods=['GET', 'POST'])
def buy(id, ticker):
    if request.method == 'GET':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        ticker = [i for i in literal_eval(ticker)]
        stock = yf.Ticker(ticker[1])
        price = stock.info['currentPrice']
        cash = user['cash']

        return render_template('/buy.html', id=id, cash=cash, price=price, stock=stock)
    elif request.method == 'POST':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        shares = request.form.get('shares')
        stock = yf.Ticker(ticker)
        price = stock.info['currentPrice']
        totalPrice = float("{:.2f}".format(float(shares) * float(price)))
        newCash = float("{:.2f}".format(float(user['cash']) - float(totalPrice)))
        timeBought = dt.datetime.now()
        dt_string = timeBought.strftime("%B %d, %Y %I:%M:%S %p")
        
        query = {'public_id' : id}
        replace = {"$set" : {'cash' : newCash}}
        user_collection.update_one(query, replace)

        add_purchase = { "$push" : {"holdings" : [ticker, shares, price, totalPrice, dt_string]}}
        user_collection.update_one(query, add_purchase)

        holdings_list = user['holdingsConsolidated']

        if len(holdings_list) > 0:
            found = 0
            for j in holdings_list:
                if ticker == j[0]:
                    j[1] = int(shares) + int(j[1])
                    j[5] = int(shares) + int(j[5])
                    j[3] = float(totalPrice) + float(j[3])
                    found = 1
            if found != 1:
                holdings_list.append([ticker, shares, price, totalPrice, dt_string, shares])
        else:
            holdings_list.append([ticker, shares, price, totalPrice, dt_string, shares])

        query = {'public_id' : id}
        add_holdings = { "$set" : {"holdingsConsolidated" : holdings_list}}
        user_collection.update_one(query, add_holdings)

        my_array = user['holdings']
        print(my_array)

        return redirect(url_for('portfolio', id=id))


@app.route("/sell/<id>/<ticker>/<totalShares>", methods=['GET', 'POST'])
def sell(id, ticker, totalShares):
    if request.method == 'GET':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        stock = yf.Ticker(ticker)
        price = stock.info['currentPrice']

        return render_template('/sell.html', id=id, totalShares=totalShares, price=price, stock=stock)
    
    elif request.method == 'POST':
        user_collection = mongo.db.Users
        user = user_collection.find_one({'public_id': id})
        shares = request.form.get('shares')
        if shares > totalShares:
            shares = totalShares
        stock = yf.Ticker(ticker)
        price = stock.info['currentPrice']
        totalPrice = float("{:.2f}".format(float(shares) * float(price)))
        newCash = float("{:.2f}".format(float(user['cash']) + float(totalPrice)))
        timeSold = dt.datetime.now()
        dt_string = timeSold.strftime("%B %d, %Y %I:%M:%S %p")

        print(totalShares)
        print(shares)

        ch_list = []
        conslHoldings = user['holdingsConsolidated']
        for i in conslHoldings:
            ch_list.append(i)
        print(ch_list)

        for i in range(len(ch_list)):
            if ch_list[i][0] == ticker:
                if int(shares) >= int(ch_list[i][1]):
                    print(i)
                    ch_list.pop(i)
                    break
                else:
                    ch_list[i][1] = int(ch_list[i][1]) - int(shares)

        print(ch_list)
                    
        
        query = {'public_id' : id}
        replace = {"$set" : {'cash' : newCash}}
        user_collection.update_one(query, replace)

        add_holdings = { "$set" : {"holdingsConsolidated" : ch_list}}
        user_collection.update_one(query, add_holdings)

        add_sale = { "$push" : {"sales" : [ticker, shares, price, totalPrice, dt_string]}}
        user_collection.update_one(query, add_sale)

        return redirect(url_for('portfolio', id=id))

@app.route("/portfolio/<id>", methods=['GET'])
def portfolio(id):
    user_collection = mongo.db.Users
    user = user_collection.find_one({'public_id': id})
    cash = user['cash']
    startingCash = user['startingCash']
    sales = list(reversed(user['sales']))
    holdings = user['holdings']
    buys = list(reversed(holdings))
    holdings_list = user['holdingsConsolidated']
    holdings_total = 0



    # for i in holdings:
    #     found = 0
    #     for j in holdings_list:
    #         if i[0] == j[0]:
    #             j[1] = int(i[1]) + int(j[1])
    #             j[3] = float(i[3]) + float(j[3])
    #             found = 1
    #     if found != 1:
    #         holdings_list.append(list(i))

    ch_list = []
    if len(holdings_list) > 0:
        for i in holdings_list:
            ch_list.append(i)
            
        

    for i in ch_list:
        # i.append(float(i[3]) / float(i[5]))
        # i.append("{:,.2f}".format(float(i[3]) / float(i[5])))
        i.append(average_share(i, id))
        stock = yf.Ticker(i[0])
        curPrice = float(stock.info['currentPrice'])
        stockTotal = float(i[1]) * curPrice
        holdings_total += stockTotal
        i.append("{:,.2f}".format(float(stockTotal)))
        i.append("{:,.2f}".format(float(curPrice)))

        percentChangeStock = round(((curPrice - float(i[6])) / float(i[6]) ) * 100, 2)
        if percentChangeStock >= 0.005:
            percentChangeStockString = f"+{round(curPrice - float(i[6]), 2)} ({percentChangeStock}%)"
        else:
            percentChangeStockString = f"{round(curPrice - float(i[6]), 2)} ({percentChangeStock}%)"
        i.append(percentChangeStockString)

    for i in holdings:
        i[3] = "{:,.2f}".format(float(i[3]))
    
    netWorth = holdings_total + cash
    print(ch_list)

    ch_list = sorted(ch_list, key=lambda x:locale.atof(x[7]))[::-1]
    
    # totalPurchasePrice = 0
    # for i in buys:
    #     totalPurchasePrice += locale.atof(i[3])

    # if totalPurchasePrice != 0:
    percentChange = round(((netWorth - startingCash) / startingCash ) * 100, 2)
    if percentChange >= 0.005:
        percentChangeString = f"+{round(netWorth - startingCash, 2)} ({percentChange}%)"
    else:
        percentChangeString = f"{round(netWorth - startingCash, 2)} ({percentChange}%)"
    # else:
    #     percentChangeString = "0.00"
    

    

    
    netWorth = ("{:,.2f}".format(float(netWorth)))
    holdings_total = ("{:,.2f}".format(float(holdings_total)))
    cash = ("{:,.2f}".format(float(cash)))

    # print(holdings_list)

    # query = {'public_id' : id}
    # add_holdings = { "$push" : {"holdingsConsolidated" : holdings_list}}
    # user_collection.update_one(query, add_holdings)

    
    return render_template('/portfolio.html', id=id, cash=cash, buys=buys, holdings=ch_list, total=holdings_total, netWorth=netWorth, percentChangeString=percentChangeString, sales=sales)




if __name__ == '__main__':
    app.run(debug=True)