# Reinforcement Learning Project

## API Key Setup
Mac -- (~/.bash_profile)
Ubuntu -- (~/git/.env/bin/activate)

## Environment Variable Settings
AlphaVantageKey=[You API key applied from AlphaVantage]
STOCK_HOME=[Home Directory For Stock]

## pip istall dependence
```buildoutcfg
sudo apt-get install python-setuptools
sudo apt install python-pip 
git clone https://github.com/peter6888/stock.git
sudo pip install virtualenv
sudo apt install python3-venv
pyvenv .env 
source .env/bin/activate
python --version
Pip install tensorflow
cd stock
pip install -r requirements.txt
sudo apt-get update && sudo apt-get install cmake libopenmpi-dev python3-dev zlib1g-dev
git clone https://github.com/openai/baselines.git
cd baseline
pip install -e .
apt-get install -y libsm6 libxext6 libxrender-dev
cp /home/peter/git/stock/baselines/run.py /home/peter/git/baselines/baselines/run.py
cp /home/peter/git/stock/gym/envs/__init__.py /home/peter/git/.env/lib/python3.6/site-packages/gym/envs/__init__.py
cp -r /home/peter/git/stock/gym/envs/stock/ /home/peter/git/.env/lib/python3.6/site-packages/gym/envsvi ~/git/.env/bin/activate
vi ~/git/.env/bin/activate
    export STOCK_HOME=/home/peter/r
    export AlphaVantageKey=[yourkey]
source ~/git/.env/bin/activate
mkdir $STOCK_HOME
cp dow_jones_30_ticker.txt $STOCK_HOME
pip install alpha_vantage
python
    import prepare_data as prd
    prd.get_data_from_av()
```
## GPU setup on Ubuntu
On GPU machine installation follow http://web.stanford.edu/class/cs234/assignment2/CS234%20Azure%20Setup.pdf

## Test for 100 times
```Test for 100 times
cd baselines
bash test_100.sh
```
