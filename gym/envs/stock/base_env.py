import numpy as np
from gym.utils import seeding
import gym
from gym import spaces
from datetime import datetime
from gym.envs.stock.stock_data import stock_data

iteration = 0
STOCK_CNT = 27
EXTRA_FEATURE_NAMES = ['vol', 'MACD', 'SAR', 'SMA', 'EMA', 'MACD_Hist', 'MACD_Signal', 'OBV','RSI']
class BaseEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, day = 0, money = 10 , scope = 1):
        self.day = day
        
        # buy or sell maximum 5 shares
        self.action_space = spaces.Box(low = -5, high = 5,shape = (STOCK_CNT,),dtype=np.int8)

        # [money]+[prices STOCK_CNT]+[owned shares STOCNK_CNT]+ EXTRA_FEACTURE_CNT * STOCK_CNT
        self.observation_space = spaces.Box(low=0, high=np.inf, shape = (STOCK_CNT*2 + len(EXTRA_FEATURE_NAMES) * STOCK_CNT + 1,))

        self.sd = stock_data()
        self.data = self.get_data()[self.day]
        
        self.terminal = False
        
        self.state = self._update_state()
        self.reward = 0
        
        self.asset_memory = [10000]
        self.buy_sell_memory = []           # (date, tic, adjusted price, attempt_shares \in [-5,5] negative is sell)
        self.confirmed_buy_sell_memory = [] # (date, tic, adjusted price, confirmed_shares \in [-5,5] negative is sell)

        self.reset()
        self._seed()

    def _update_state(self):
        self.state =  [10000 if self.day==0 else self.state[0]] + self.data.adjcp.values.tolist() + list(self._get_current_holdings())
        if len(EXTRA_FEATURE_NAMES) > 0:
            for feature in EXTRA_FEATURE_NAMES:
                self.state += self.data[feature].values.tolist()
        return self.state


    def _sell_stock(self, index, action):
        self.buy_sell_memory.append((self.data.date[index], self.data.tic[index], self.data.adjcp[index], action))
        if self.state[index+STOCK_CNT+1] > 0:
            self.state[0] += self.state[index+1]*min(abs(action), self.state[index+STOCK_CNT+1])
            self.confirmed_buy_sell_memory.append((self.data.date[index], self.data.tic[index], self.data.adjcp[index], -min(abs(action), self.state[index+STOCK_CNT+1])))
            self.state[index+STOCK_CNT+1] -= min(abs(action), self.state[index+STOCK_CNT+1])
        else:
            pass
    
    def _buy_stock(self, index, action):
        self.buy_sell_memory.append((self.data.date[index], self.data.tic[index], self.data.adjcp[index], action))
        available_amount = self.state[0] // self.state[index+1]
        # print('available_amount:{}'.format(available_amount))
        if min(available_amount, action) > 0:
            self.confirmed_buy_sell_memory.append((self.data.date[index], self.data.tic[index], self.data.adjcp[index], min(available_amount, action)))
        self.state[0] -= self.state[index+1]*min(available_amount, action)
        # print(min(available_amount, action))
        self.state[index+STOCK_CNT+1] += min(available_amount, action)

    def step(self, actions):
        # print(self.day)
        # print(actions)

        self.terminal = self.reached_terminal(self.day)
        if self.reached_terminal(self.day):
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.save_results(timestamp)
            print('total asset: {}'.format(self.state[0] + sum(np.array(self.state[1:STOCK_CNT+1]) * np.array(
                self._get_current_holdings()))))
            return self.state, self.reward, self.terminal, {}

        else:
            # print(np.array(self.state[1:STOCK_CNT+1]))


            begin_total_asset = self.state[0]+ sum(np.array(self.state[1:STOCK_CNT+1]) * np.array(
                self._get_current_holdings()))
            # print("begin_total_asset:{}".format(begin_total_asset))
            argsort_actions = np.argsort(actions)
            sell_index = argsort_actions[:np.where(actions < 0)[0].shape[0]]
            buy_index = argsort_actions[::-1][:np.where(actions > 0)[0].shape[0]]

            for index in sell_index:
                #print('take sell action'.format(actions[index]))
                self._sell_stock(index, actions[index])

            for index in buy_index:
                # print('take buy action: {}'.format(actions[index]))
                self._buy_stock(index, actions[index])

            self.day += 1
            self.data = self.get_data()[self.day]


            # print("stock_shares:{}".format(self.state[STOCK_CNT+1:]))
            self.state = self._update_state()

            end_total_asset = self.state[0]+ sum(np.array(self.state[1:STOCK_CNT+1]) * np.array(self._get_current_holdings()))
            # print("end_total_asset:{}".format(end_total_asset))
            
            self.reward = end_total_asset - begin_total_asset            
            # print("step_reward:{}".format(self.reward))

            self.asset_memory.append(end_total_asset)


        return self.state, self.reward, self.terminal, {}

    def _get_current_holdings(self):
        if self.day == 0:
            return [0 for _ in range(STOCK_CNT)]
        return self.state[STOCK_CNT + 1:2*STOCK_CNT + 1]

    def reset(self):
        self.asset_memory = [10000]
        self.day = 0
        self.data = self.get_data()[self.day]
        self.state = self._update_state()
        
        # iteration += 1 
        return self.state
    
    def render(self, mode='human'):
        return self.state

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def get_data(self):
        pass

    def reached_terminal(self, day):
        pass

    def save_results(self, timestamp):
        pass
