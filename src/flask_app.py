import pandas as pd

from flask import Flask, escape, request
from flask import render_template

import marketDB

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

market_db = marketDB.MarketDB()


@app.route("/")
def home():
    stock_filter = request.args.get("filter", False)
    if stock_filter:
        stock_df = market_db.getFilteredStock(stock_filter)
        return render_template("index.html", stocks=market_db.codes)
    else:
        return render_template("index.html", stocks=market_db.codes)


@app.route("/stock/<name>", methods=["get", "post"])
def get_company_stock(name):
    data = market_db.getDailyPrice(name)
    stocks = market_db.makeStockLists(data)
    strategies = pd.read_sql("select * from strategy", market_db.conn)
    strategies = strategies.values.tolist()

    return render_template(
        "stock_detail.html",
        name=name,
        stocks=stocks,
        length=len(stocks),
        strategies=strategies,
    )


# @app.route("/apply_strategy", methods=['post'])
# def dispatch_request(self):
#     if request.method == 'GET':
#         bar=request.args.get('foo', 'bar')
#
# if request.method == 'POST':
#     bar=request.form.get('foo', 'bar')

if __name__ == "__main__":
    app.run(port=5000, debug=True)
