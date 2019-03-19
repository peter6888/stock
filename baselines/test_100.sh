#!/bin/bash
for (( c=1; c<=100; c++ ))
do  
   echo "Run $c times"
   python -m baselines.run --alg=ddpg --env=Stock-v0 --network=mlp --num_timesteps=1e4 --play
done
