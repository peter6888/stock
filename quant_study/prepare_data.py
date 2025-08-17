
''' Below commands are very helpful, I use it few of times after each of my experiment. Keep it here!
import readline
for i in range(readline.get_current_history_length()):
    print(readline.get_history_item(i + 1))
'''

from os import listdir, environ, mkdir
from os.path import isfile, isdir, join
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

csv_dir = '{}/{}'.format(environ['STOCK_HOME'], 'csv')
ti_dir = '{}/{}'.format(environ['STOCK_HOME'], 'ti')
stock_home = environ['STOCK_HOME']
def union_data_to_one_csv():
    onlyfiles = [f for f in listdir(csv_dir) if isfile(join(csv_dir, f)) and f[-3:]=='csv']
    assert len(onlyfiles)==30
    ti_names = ['mcd', 'sar', 'sma', 'ema', 'rsi', 'obv']
    stock_data_list = []
    for f in onlyfiles:
        tic = f[:-4]
        stock_data = pd.read_csv("{}/{}".format(csv_dir, f))
        stock_data['tic'] = tic
        for ti in ti_names:
            ti_data = pd.read_csv("{}/{}_{}.csv".format(ti_dir, tic, ti))
            stock_data = pd.merge(stock_data, ti_data, on='date', how='left')
        stock_data_list.append(stock_data)

    u_data = pd.concat(stock_data_list)
    sorted_data = u_data.sort_values(['date','tic'])
    print('union and sort all stocks to {}/30.csv'.format(stock_home))
    sorted_data.to_csv('{}/30.csv'.format(stock_home))

def get_data_from_av():
    '''
    Get live date from Alpha Vantage, and store as *.csv files under $STOCK_HOME/csv subfolder
    :return:
    '''
    if not isdir(csv_dir):
        mkdir(csv_dir)
    ts = TimeSeries(key=environ['AlphaVantageKey'], output_format='pandas')
    ti = TechIndicators(key=environ['AlphaVantageKey'], output_format='pandas')
    index_name2fun_dict = {'mcd':ti.get_macd, 'sma':ti.get_sma, 'ema':ti.get_ema, 'rsi':ti.get_rsi, \
                           'sar':ti.get_sar, 'obv':ti.get_obv}
    print('Load ^DJI to {}/^DJI.csv'.format(stock_home))
    ts.get_daily_adjusted('^DJI', 'full')[0].to_csv("{}/^DJI.csv".format(stock_home))
    time.sleep(20)
    tickers = get_tickers()
    for tic in tickers:
        _data, _ = ts.get_daily_adjusted(tic, 'full')
        _data.to_csv('{}/{}.csv'.format(csv_dir, format(tic)))
        print('Load {} to dir {}'.format(tic, csv_dir))
        time.sleep(20)
        for index_name in index_name2fun_dict.keys():
            _tidata, _ = index_name2fun_dict[index_name](tic)
            ti_filename = "{}/{}_{}.csv".format(ti_dir, tic, index_name)
            _tidata.to_csv(ti_filename)
            print('Save to {}'.format(ti_filename))
            time.sleep(20)

    # zip -r tickers.zip csv
    # scp peter@65.52.17.108:/home/peter/tickers.zip tickers.zip

def get_tickers():
    with open('{}/dow_jones_30_ticker.txt'.format(stock_home)) as f:
        tickers = f.readlines()
    tickers = [x.strip() for x in tickers]
    return tickers

def is_latest():
    '''
    Check if stock data been updated to lastest or not created
    :return:
    '''
    lastupdate_filename = '{}/.lastupdate'.format(stock_home)
    lastupdate = Path(lastupdate_filename)
    if lastupdate.is_file():
        with open(lastupdate_filename, 'r') as f:
            lastupdate_date = f.readline()
            if lastupdate_date == datetime.now().date().isoformat():
                return True
            elif datetime.now().date().weekday() > 5:
                return True
    return False

def union_run_results(folder='/Users/pe.li/results'):
    '''
    Tool to union run results and process before draw it out
    :return:
    '''
    result_files = [f for f in listdir(folder) if isfile(join(folder, f)) and f[-3:] == 'txt']
    result_data_list = []
    for f in result_files:
        result_data_list.append(pd.read_csv('{}/{}'.format(folder, f), header=None))
    u_data = pd.concat(result_data_list)
    u_data = u_data.transpose()
    u_data.to_csv("{}/result_data.csv".format(folder), header=None)
    print('Wrote to:{}/result_data.csv'.format(folder))

if __name__ == "__main__":
    if not is_latest():
        get_data_from_av()
        union_data_to_one_csv()
        f = open('{}/.lastupdate'.format(stock_home), 'w')
        f.write(datetime.now().date().isoformat())
        f.close()
    else:
        print("Already latest, need need update.")


