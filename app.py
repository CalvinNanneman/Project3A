import csv
from flask import Flask, render_template, request, url_for, flash, redirect, abort
from datetime import datetime
import requests
from lxml import html
import pygal


#make flask app object
app = Flask(__name__)
app.config["DEBUG"] = True



#import stock list from csv
def import_symbols():
    with open('stocks.csv', 'r') as file:
        reader = csv.reader(file)
        symbols = [row[0] for row in reader]
    return symbols

def get_chart(symbol, chart_type, time_series, start_date, end_date):
    
    api_key = 'FWOGPIULQ1FC1KXE'
    symbolA = str(symbol)
    url = f'https://www.alphavantage.co/query?function={time_series}&symbol={symbolA}&apikey={api_key}'

    time_series_output = ""
    if time_series == "TIME_SERIES_INTRADAY":
        time_series_output = "Time Series (5min)"
    if time_series == "TIME_SERIES_DAILY":       
        time_series_output = "Time Series (Daily)"
    if time_series == "TIME_SERIES_WEEKLY":   
        time_series_output = "Weekly Time Series"
    if time_series == "TIME_SERIES_MONTHLY":
        time_series_output = "Monthly Time Series"

    print(symbol, chart_type, time_series, start_date, end_date)

    response = requests.get(url)
    data = response.json()
    print(data)

    # Parse the API response
    tree = html.fromstring(response.text)
    closing_prices = []
    for date, values in data[time_series_output].items():
        closing_prices.append(float(values['4. close']))

    print(closing_prices)
    # Create a line chart
    if chart_type == "line":
        chart = pygal.Line()
        chart.title = f'{symbol} Stock Prices'
        chart.x_labels = reversed([str(i) for i in range(1, len(closing_prices) + 1)])
        chart.add('Closing Price', [float(price) for price in closing_prices])

        # Render the chart to an SVG file
        chart.render_to_file('stock_chart.svg')

        #webbrowser.open('stock_chart.svg')

    #create bar chart
    if chart_type == "bar":
        chart = pygal.Bar()
        chart.title = f'{symbol} Stock Prices'
        chart.x_labels = reversed([str(i) for i in range(1, len(closing_prices) + 1)])
        chart.add('Closing Price', [float(price) for price in closing_prices])

        # Render the chart to an SVG file
        chart.render_to_file('stock_chart.svg')
        
        #webbrowser.open('stock_chart.svg')


#display index page
@app.route('/' , methods=['GET', 'POST'])
def index():
    symbols = import_symbols()

    if request.method == 'POST':
        #getting user input
        symbol = request.form['symbol']
        chart_type = request.form['chartType']
        time_series = request.form['timeSeries']
        start_date = request.form['startDate']
        end_date = request.form['endDate']

        #call function to get graph
        get_chart(symbol, chart_type, time_series, start_date, end_date)

        # Display user input below the form
        user_input_html = f"Symbol: {symbol}, Chart Type: {chart_type}, Time Series: {time_series}, Start Date: {start_date}, End Date: {end_date}"
        return render_template('index.html', symbols=symbols, userInput=user_input_html)

    return render_template('index.html', symbols=symbols)


   
app.run(host="0.0.0.0")