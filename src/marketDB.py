import pymysql
import os, re
import pandas as pd

from dotenv import load_dotenv
from datetime import date, datetime, timedelta


class MarketDB:
    def __init__(self):
        load_dotenv(verbose=True)
        db_name = os.getenv("MARIADB_NAME")
        db_port = int(os.getenv("MARIADB_PORT"))
        db_passwd = os.getenv("MARIADB_PASSWD")

        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password=db_passwd,
            db=db_name,
            port=db_port,
            charset="utf8",
        )
        self.codes = dict()
        self.createStockTable()
        self.getCompanyInfo()

    def __del__(self):
        self.conn.close()

    def createStockTable(self):
        with self.conn.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS company (
                code VARCHAR(20),
                name VARCHAR(40),
                last_update DATE,
                PRIMARY KEY (code))
                COLLATE='utf8_general_ci';
            """
            cursor.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS price (
                code VARCHAR(20),
                date DATE,
                open BIGINT(20),
                high BIGINT(20),
                low BIGINT(20),
                close BIGINT(20),
                diff BIGINT(20),
                volume BIGINT(20),
                PRIMARY KEY (code, date))
                COLLATE='utf8_general_ci';
            """
            cursor.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS strategy (
                id INTEGER PRIMARY KEY,
                name VARCHAR(40) NOT NULL)
                COLLATE='utf8_general_ci';
            """
            cursor.execute(sql)
            sql = """
            CREATE TABLE IF NOT EXISTS stock_strategy (
                stock_code VARCHAR(20) NOT NULL,
                strategy_id INTEGER NOT NULL,
                foreign key (stock_code) references company(code),
                foreign key (strategy_id) references strategy(id))
                COLLATE='utf8_general_ci';
            """
            cursor.execute(sql)

            strats_ = ["opening_breakout", "opening_breakdown"]
            df = pd.read_sql("select * from strategy", self.conn)
            if df is None:
                for idx_, strategy in enumerate(strats_):
                    sql = f"INSERT INTO strategy (id, name) VALUES ('{idx_}', '{strategy}')"
                    cursor.execute(sql)

        self.conn.commit()
        pass

    def getCompanyInfo(self):
        sql = "SELECT * FROM company"
        companyInfo = pd.read_sql(sql, self.conn)
        for idx_ in range(len(companyInfo)):
            self.codes[companyInfo["code"].values[idx_]] = companyInfo["name"].values[idx_]

    def getDailyPrice(self, code, start_date=None, end_date=None):
        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime("%Y-%m-%d")
            print(f"start_date is initialized to '{start_date}'")
        else:
            start_lst = re.split("\D+", start_date)
            if start_lst[0] == "":
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > 2200:
                print(f"ValueError: start_year({start_year:d}) is wrong.")
                return
            if start_month < 1 or start_month > 12:
                print(f"ValueError: start_month({start_month:d}) is wrong.")
                return
            if start_day < 1 or start_day > 31:
                print(f"ValueError: start_day({start_day:d}) is wrong.")
                return
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"

        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")
            print(f"end_date is initialized to '{end_date}'")
        else:
            end_lst = re.split("\D+", end_date)
            if end_lst[0] == "":
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1800 or end_year > 2200:
                print(f"ValueError: end_year({end_year:d}) is wrong.")
                return
            if end_month < 1 or end_month > 12:
                print(f"ValueError: end_month({end_month:d}) is wrong.")
                return
            if end_day < 1 or end_day > 31:
                print(f"ValueError: end_day({end_day:d}) is wrong.")
                return
            end_date = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"

        codes_keys = list(self.codes.keys())
        codes_values = list(self.codes.values())
        if code in codes_keys:
            pass
        elif code in codes_values:
            idx_ = codes_values.index(code)
            code = codes_keys[idx_]
        else:
            print(f"ValueError: Code({code}) doesn't exist.")
        sql = (
            f"SELECT * FROM price WHERE code = '{code}'"
            f" and date >= '{start_date}' and date <= '{end_date}'"
        )
        df = pd.read_sql(sql, self.conn)
        return df.sort_index(ascending=False)

    def getFilteredStock(self, stock_filter):
        today = date.today().isoformat()
        sql = (
            f"with pd as (SELECT price.code, company.name, MAX(price.close), date "
            f"FROM price JOIN company ON price.code = company.code "
            f"GROUP BY price.code) "
            f"SELECT * FROM pd WHERE DATE = '{today}';"
        )
        df = pd.read_sql(sql, self.conn)
        print(df, stock_filter, today)


if __name__ == "__main__":
    market_db = MarketDB()
    # print(len(market_db.codes))
    # for idx, code in enumerate(market_db.codes):
    #     print(idx, code, market_db.codes[code])

    # for idx, stock in market_db.codes.items():
    #     print(idx, stock)

    # print(market_db.codes)
    # print(market_db.codes.keys())
    # print(market_db.codes.values())

    data = market_db.getDailyPrice("000020", "2021-02-12", "2021-02-23")
    data_list = data.values.tolist()
    print(data_list)
    for x in data_list:
        print(x[1])
        print(x[2])
        print(x[3])
        print(x[4])
        print(x)

    # data = data.to_dict()
    # print(len(data))
    # print(data["open"])
    # print(len(data["open"]))
    # print(data.keys())
    # print(data.values())
    # for key in data.keys():
    #     print(data[key])
    # for key, value in data.items():
    #     print(key, value)
    #     print("--------------")

    #
    # market_db.getFilteredStock(None)

    # strats = pd.read_sql("select * from strategy", market_db.conn)
    # strats = strats.to_dict()
    # print(strats.items())

    # for x in s_dict.keys():
    #     print(x)
    # for x in s_dict.values():
    #     print(x)
    #
    # for key, value in strategies.iteritems():
    #     print(key)
    #     print(value)
    #     print("---------------")
    #
    # s_json = strategies.to_json(orient="values")
    # print(s_json)
