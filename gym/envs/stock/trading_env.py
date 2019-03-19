from gym.envs.stock.base_env import BaseEnv
from os import environ
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

stock_home = environ['STOCK_HOME']
_lambda = 1
class StockEnv(BaseEnv):
    def __init__(self, day=0, money=10, scope=1):
        self.r_dct = defaultdict(list)
        self.it_cnt = -1
        super().__init__(day, money, scope)

    def step(self, actions):
        super().step(actions)
        if not self.reached_terminal(self.day):
            self.r_dct[self.day].append(self.reward)
            if np.var(self.r_dct[self.day]) > 0:# and np.log(np.var(self.r_dct[self.day])) > 0:
                self.reward = self.reward - np.log(1+np.var(self.r_dct[self.day])) * _lambda
        return self.state, self.reward, self.terminal, {}

    def reset(self):
        self.it_cnt = self.it_cnt + 1
        # for k,v in self.r_dct.items():
        #    print("{} var={} log(var)={} {}".format(k, np.var(v), np.log(np.var(v)), len(v)))
        super().reset()
        return self.state

    def get_data(self):
        return self.sd.get_training_daily_data()

    def reached_terminal(self, day):
        return day >= 1761

    def save_results(self, timestamp):
        plt.plot(self.asset_memory, 'r')
        plt.savefig('{}/{}.png'.format(stock_home, timestamp))
        plt.close()


