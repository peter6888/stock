'''
These unit test to validate the stock data details
-- stock date
-- stock adjusted price
-- ticks
which are used by the environments
'''
from stock_data import stock_data
if __name__ == "__main__":
    sd = stock_data()
    training_daily_data = sd.get_training_daily_data()
    this_day = training_daily_data[0]
    print(this_day.adjcp.values.tolist())
    '''
    PRCCD	NUM	PRCCD -- Price - Close - Daily
    PRCHD	NUM	PRCHD -- Price - High - Daily
    PRCLD	NUM	PRCLD -- Price - Low - Daily
    PRCOD	NUM	PRCOD -- Price - Open - Daily
    
    AJEXDI	NUM	AJEXDI -- Adjustment Factor (Issue)-Cumulative by Ex-Date
    
    data_3['adjcp'] = data_3['prccd'] / data_3['ajexdi']
    adjcp -- Adjust Close Price
    '''
    STOCK_CNT = 27
    print("Test self.train_daily_data[self.day]")
    assert len(training_daily_data[0]) > 0
    print("training_daily_data[0]={}".format(training_daily_data[0]))
    print("Test self.data.adjcp.values.tolist()")
    assert len(training_daily_data[-1].adjcp.values.tolist()) == STOCK_CNT
    print("len(training_daily_data[-1].adjcp.values.tolist() is {})={}".format(\
        training_daily_data[-1].adjcp.values.tolist(), \
        len(training_daily_data[-1].adjcp.values.tolist())))
    print("Test for each stock have length of STOCK_CNT")
    for stock in training_daily_data:
        assert len(stock.adjcp.values.tolist())==STOCK_CNT
    print("Test self.terminal = self.day >= 1761 for upper boundary of data")
    assert len(training_daily_data) >= 1761
    print("len(training_daily_data)=={}".format(len(training_daily_data)))
    print("Test tic are in order.")
    tic_list = training_daily_data[0].tic.tolist()
    for tdd in training_daily_data:
        assert tdd.tic.tolist() == tic_list

    print("Test DJI Growth")
    growth = sd.get_baseline_dji_growth()
    print("Len(growth)={}".format(len(growth)))
    print("Test Test Data Size")
    test_daily_data = sd.get_test_daily_data()
    print("Len(Test)={}".format(len(test_daily_data)))
    print('Test both training and test data has vol column')
    print(training_daily_data[-1].columns)
    assert len(training_daily_data[-1].vol.values.tolist()) > 0

    assert len(test_daily_data[-1].vol.values.tolist()) > 0
    print('Test data has MACD')
    assert len(training_daily_data[-1].MACD.values.tolist()) > 0
