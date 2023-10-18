# filename: stock_price_plot.py

import yfinance as yf
import matplotlib.pyplot as plt
import datetime

# Get today's date
today = datetime.date.today()

# Get the date one year ago
one_year_ago = today - datetime.timedelta(days=365)

# Download the stock data
nvda = yf.download('NVDA', start=one_year_ago, end=today)
tsla = yf.download('TSLA', start=one_year_ago, end=today)

# Plot the data
plt.figure(figsize=(14, 7))
plt.plot(nvda['Close'], label='NVDA')
plt.plot(tsla['Close'], label='TSLA')
plt.title('NVDA vs TSLA Stock Price YTD')
plt.xlabel('Date')
plt.ylabel('Price ($)')
plt.legend()
plt.grid(True)
plt.show()