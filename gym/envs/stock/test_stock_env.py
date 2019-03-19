from stock_data import stock_data
if __name__ == "__main__":
    h = '/Users/pe.li/git/rl_project/Data_Daily_Stock_Dow_Jones_30'
    sd = stock_data(h)
    print("Testing load training data")
    dd = sd.get_training_daily_data()
    print("len(training data)=={}".format(len(dd)))
    assert len(dd) > 0
    print("Testing load test data")
    tt = sd.get_test_daily_data()
    print("len(test data)=={}".format(len(tt)))
    assert len(tt) > 0
    print("Testing load and calculate DJI growth")
    dji_growth = sd.get_baseline_dji_growth()
    print("len(dji growth)=={}".format(len(dji_growth)))
    assert len(dji_growth) > 0