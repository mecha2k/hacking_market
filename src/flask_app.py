from flask import Flask, escape, request
from flask import render_template

import marketDB

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

market_db = marketDB.MarketDB()


@app.route("/")
def home():
    stock_filter = request.args.get("filter", False)
    if stock_filter == "intraday_highs":
        pass

    return render_template("index.html", stocks=market_db.codes)


@app.route("/stock/<name>")
def get_company_stock(name):
    data = market_db.getDailyPrice(name)
    return render_template(
        "stock_detail.html", name=name, company_stock=data.values.tolist(), length=len(data)
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
