cp __init__.py %env%/lib/python3.6/site-packages/gym/__init__.py
cp -r stock_env %env%/lib/python3.6/site-packages/gym/envs/zxstock
```update gym enviornment
~/git/.env/lib/python3.6/site-packages/gym/envs$ cp /home/peter/git/rl_project/gym/envs/__init__.py .
~/git/.env/lib/python3.6/site-packages/gym/envs$ cp -r /home/peter/git/rl_project/gym/envs/stock .
```
```update baselines run.py
~/git/baselines/baselines$ cp /home/peter/git/rl_project/baselines/run.py .
```