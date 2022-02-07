from threading import Timer
from datetime import datetime
import pandas as pd
from flask import Flask, jsonify
import requests

APP_NAME = "CryptoWat Tracker"
# TIMER_THRESHOLD = 5
TIMER_THRESHOLD = 60


class RepeatTimer(Timer):

    def run(self):
        while not self.finished.wait(self.interval):
            self.function()


class CryptoDataTracker:

    def __init__(self):
        self.data = {}
        self.app = Flask(APP_NAME)
        self._start_timer()
        self._run_flask()

    def _start_timer(self):
        """
        Just initializing the thread repeater for querying the data from the criptoWat's API
        """
        timer = RepeatTimer(TIMER_THRESHOLD, self._get_market_metrics)
        timer.start()

    def _get_market_metrics(self):
        """
        Adding the data of every metric's markets to the 'data' var.
        The keys of the data are the metrics, the values are PD DFs in the pattern:
            {'update_time': datetime, MARKET1: float (MARKET1's price), MARKET2: float, Etc.}
        TODO: when the business meaning of the markets will be clear, change the variable matching to this meaning
        """
        update_time = datetime.utcnow()
        data_json = requests.get("https://api.cryptowat.ch/markets/prices").json()
        basic_df = self._get_dict_from_prices(data_json)
        # for metric in ['btcusd', 'zrxbusd']:
        for metric in basic_df.index:
            metric_df = pd.DataFrame([basic_df.loc[metric].iloc[0]])
            metric_df['update_time'] = update_time
            self.data[metric] = pd.concat([self.data.get(metric, pd.DataFrame()), metric_df])

    @staticmethod
    def _get_dict_from_prices(data_json):
        """
        Transforming the output of the API into a DF indexed with the metrics and contains the markets' prices
        :param data_json: the output of cryptoWat's API
        :return: DF
        """
        basic_df = pd.DataFrame.from_dict(data_json['result'], orient='index')
        basic_df = basic_df[basic_df.index.str.startswith('market')]
        index_as_str = basic_df.index.str.split(":").str
        basic_df['metric'] = index_as_str[2]
        basic_df.index = index_as_str[1]
        basic_df = basic_df.groupby('metric').agg(dict)
        return basic_df

    def _run_flask(self):
        self.app.add_url_rule('/restart_data', 'restart_data', self.restart_data, methods=['POST'])
        self.app.add_url_rule('/get_metrics', 'get_metrics', lambda: jsonify(self.data.keys()), methods=['GET'])
        self.app.add_url_rule('/get_price/<metric>', 'get_price', self.get_price, methods=['GET'])
        self.app.add_url_rule('/get_rank/<metric>', 'get_rank', self.get_rank, methods=['GET'])
        self.app.add_url_rule('/get_data', 'get_data', self.get_data, methods=['GET'])
        self.app.run()

    def restart_data(self):
        del self.data
        self.data = {}
        return jsonify(None)

    def get_data(self):
        data_as_json = self.data.copy()
        for metric, df in data_as_json.items():
            data_as_json[metric] = df.to_dict('records')
        return jsonify(data_as_json)

    def get_price(self, metric):
        df = self.data.get(metric)
        if df is None:
            return jsonify(False)
        return jsonify(df.to_dict('records'))

    def get_rank(self, metric):
        df = self.data.get(metric)
        if df is None:
            return jsonify(False)
        return jsonify(df.std().to_dict())


if __name__ == '__main__':
    cr = CryptoDataTracker()
    pass
