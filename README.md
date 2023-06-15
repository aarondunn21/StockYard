This application is a stock simulator built with the Flask framework and uses the Yahoo Finance API for real-time stock market data.
User's can make an account that is persistent in a MongoDB Atlas cloud database. In the registration process, they choose their starting cash for the simulatation.
The user is greeted by a home screen with some pre-loaded popular stock tickers, and a search bar to find a specific stock.
On the stock's page, real time data is displayed and a interactive candlestick chart is generated with Plotly and embeded in the page.
Further, the user can press the buy button to purchase shares with their simulated cash on hand.
Once purchased, the user is taken to their portfolio page to view their simulated net worth and share holding break down.
On the portfolio page, they can also choose to sell their shares of a stock to convert their profits to cash for further simulation.
