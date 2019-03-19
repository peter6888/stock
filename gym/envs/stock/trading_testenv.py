import matplotlib.pyplot as plt
from os import environ, mkdir
from os.path import isdir
from datetime import datetime
from gym.envs.stock.base_env import BaseEnv

stock_home = environ['STOCK_HOME']

class StockTestEnv(BaseEnv):
    def __init__(self, day=0, money=10, scope=1):
        super().__init__(day, money, scope)

    def get_data(self):
        return self.sd.get_test_daily_data()

    def reached_terminal(self, day):
        return day >= 794#685

    def save_results(self, timestamp):
        plt.plot(self.asset_memory, 'r')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%s')
        if not isdir('{}/results'.format(stock_home)):
            mkdir('{}/results'.format(stock_home))
        print('Write asset sequence to {}/results/{}.txt'.format(stock_home, timestamp))
        with open('{}/results/{}.txt'.format(stock_home, timestamp), 'w') as f:
            f.write(','.join([str(asset) for asset in self.asset_memory]))
        self._save_buysell(self.buy_sell_memory, 'buysell', timestamp)
        self._save_buysell(self.confirmed_buy_sell_memory, 'confirmed', timestamp)
        dji_account_growth = self.sd.get_baseline_dji_growth()
        plt.plot(dji_account_growth)
        plt.savefig('{}/results/test_{}.png'.format(stock_home, timestamp))
        plt.close()

    def _save_buysell(self, transaction, file_ext, timestamp):
        print('Write {} sequence to {}/results/{}.{}'.format(file_ext, stock_home, timestamp, file_ext))
        with open('{}/results/{}.txt.{}'.format(stock_home, timestamp, file_ext), 'w') as f:
            f.write('\n'.join([','.join([str(date), tic, str(adjcp), str(share)]) for (date, tic, adjcp,share) in transaction]))



