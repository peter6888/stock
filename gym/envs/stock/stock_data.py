import numpy as np
import pandas as pd
from datetime import datetime
from os import environ

stock_home = environ['STOCK_HOME']
class stock_data():
    def __init__(self, csv_home=stock_home, test_start=20160101):
        self.training_daily_data = []
        self.test_daily_data = []
        self.account_growth = []
        self.stock_home = csv_home
        self.test_start = test_start
        self.test_start_date = datetime(test_start//10000, test_start%10000//100, test_start%100)

    def get_training_daily_data(self):
        self._conditional_data_init()
        return self.training_daily_data

    def get_test_daily_data(self):
        self._conditional_data_init()
        return self.test_daily_data

    def get_baseline_dji_growth(self):
        if len(self.account_growth)>0:
            return self.account_growth

        dji = self.get_dji_data_av()
        test_dji = dji[dji['Date'] > '2016-01-01']
        dji_price = test_dji['Adj Close']
        daily_return = dji_price.pct_change(1)
        daily_return = daily_return[1:]
        daily_return.reset_index()
        initial_amount = 10000

        total_amount = initial_amount
        self.account_growth.append(initial_amount)
        for i in range(len(daily_return)):
            total_amount = total_amount * daily_return.iloc[i] + total_amount
            self.account_growth.append(total_amount)
        return self.account_growth

    def get_dji_data(self):
        return pd.read_csv(
            "{0}/^DJI.csv".format(self.stock_home))

    def get_dji_data_av(self):
        dji = pd.read_csv(
            "{0}/^DJI.csv".format(self.stock_home))
        dji['Date'] = dji['date']
        dji['Adj Close'] = dji['5. adjusted close']
        return dji


    def _conditional_data_init(self):
        if len(self.training_daily_data) == 0:
            self.training_daily_data, self.test_daily_data = self.data_init_av()

    def data_init(self):
        data_1 = pd.read_csv('{0}/dow_jones_30_daily_price.csv'.format(self.stock_home))
        equal_4711_list = list(data_1.tic.value_counts() == 4711)
        names = data_1.tic.value_counts().index
        # select_stocks_list = ['NKE','KO']
        select_stocks_list = list(names[equal_4711_list])+['NKE','KO']
        data_2 = data_1[data_1.tic.isin(select_stocks_list)][~data_1.datadate.isin(['20010912','20010913'])]
        #data_3 = data_2[['iid','datadate','tic','prccd','ajexdi', 'adjcp']]
        data_3 = data_2[['datadate', 'tic', 'adjcp']]
        #data_3['adjcp'] = data_3['prccd'] / data_3['ajexdi']
        train_data = data_3[(data_3.datadate > 20090000) & (data_3.datadate < 20160000)]
        test_data = data_3[data_3.datadate > 20160000]

        for date in np.unique(train_data.datadate):
            self.training_daily_data.append(train_data[train_data.datadate == date])

        for date in np.unique(test_data.datadate):
            self.test_daily_data.append(test_data[test_data.datadate == date])

        return self.training_daily_data, self.test_daily_data

    def data_init_av(self):
        data_1 = pd.read_csv('{}/30.csv'.format(self.stock_home))
        equal_5324_list = list(data_1.tic.value_counts() == 5327)
        names = data_1.tic.value_counts().index
        data_2 = data_1[data_1.tic.isin(list(names[equal_5324_list]))]
        data_3 = data_2[['date', 'tic', '5. adjusted close', '6. volume', 'EMA', 'MACD', 'MACD_Hist', 'MACD_Signal', 'OBV','RSI','SAR',	'SMA']]
        data_3 = data_3.rename(index=str, columns={'5. adjusted close': 'adjcp', '6. volume':'vol'})
        data_3['DD'] = pd.to_datetime(data_3.date)
        data_3['datadate'] = data_3['DD'].dt.strftime('%Y%m%d')
        data_3['datadate'] = pd.to_numeric(data_3['datadate'])

        train_data = data_3[(data_3.datadate > 20090000) & (data_3.datadate < 20160000)]
        test_data = data_3[data_3.datadate > 20160000]

        for date in np.unique(train_data.datadate):
            self.training_daily_data.append(train_data[train_data.datadate == date])

        for date in np.unique(test_data.datadate):
            self.test_daily_data.append(test_data[test_data.datadate == date])

        return self.training_daily_data, self.test_daily_data


