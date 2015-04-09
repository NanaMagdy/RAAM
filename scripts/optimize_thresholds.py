"""
Compute optimal thresholds for the given configuration
"""

import raam.examples
import configuration
import numpy as np
import random 
import math

_epsilon = 1e-6

def _eval_dimchange(sim,lowers,uppers,dim,l,u,horizon,runs):
    """ Evaluates the dimension change impact """
    dim_lowers = lowers.copy()
    dim_uppers = uppers.copy()
    
    dim_lowers[dim] = l
    dim_uppers[dim] = u
    
    policy = raam.examples.inventory.threshold_policy(dim_lowers, dim_uppers, sim)
    
    # Common random numbers for the evaluation!
    np.random.seed(0)
    random.seed(0)
    
    samples = sim.simulate(horizon,policy,runs)
    
    print('.', end='')
    return samples.statistics(sim.discount)['mean_return']


def optimize_jointly(sim,step=0.1,horizon=600,runs=5):
    """
    Jointly optimizes uppen and lower thresholds for charging and discharging for 
    each dimension.
    
    It can be shown (a publication pending) that this method will compute
    the optimal solution when the battery degradation function satisfies some
    somewhat restrictive properties.
    """
    
    values = [(l,u) for l in np.arange(0,1+step/2,step) for u in np.arange(l,1+step/2,step) ]
    
    # copy the lower and upper bounds
    lowers = np.zeros(len(sim.price_buy))    # lower thresholds
    uppers = np.ones(len(sim.price_buy))     # upper thresholds
   
    for iteration in range(10):
        print('Lowers', lowers)
        print('Uppers', uppers)
        
        for dimension in range(len(sim.price_sell)):
            print('Dimension', dimension)
            returns = [_eval_dimchange(sim,lowers,uppers,dimension,l,u,horizon,runs) for (l,u) in values]
            
            maxindex = np.argmax(returns)
            
            print('\n', returns[maxindex])
            l,u = values[maxindex]
            lowers[dimension] = l
            uppers[dimension] = u
    
    print('Lowers', lowers)
    print('Uppers', uppers)


def optimize_independently(sim,step=0.1,horizon=600,runs=5):
    """
    Optimizes the upper and lower thresholds independently. It is not clear 
    that this method actually computes the optimal policy        
    """
    
    # copy the lower and upper bounds
    lowers = 0.5*np.ones(len(sim.price_buy))    # lower thresholds
    uppers = 0.5*np.ones(len(sim.price_buy))     # upper thresholds
    
    
    for iteration in range(10):
        print('Lowers', lowers)
        print('Uppers', uppers)
        
        weight = 1.0 / math.sqrt(iteration + 1)
        
        for dimension in range(len(sim.price_sell)):
            print('Dimension', dimension)
            
            print('   lowers')
            values = np.arange(0,1+_epsilon,step)
            if len(values) > 0:
                returns = [_eval_dimchange(sim,lowers,uppers,dimension,\
                            l,max(l,uppers[dimension]),horizon,runs)\
                             for l in values]
                maxindex = np.argmax(returns)
                l = values[maxindex]
                lowers[dimension] = weight * l + (1-weight)*lowers[dimension]
                uppers[dimension] = max(uppers[dimension],lowers[dimension])
                assert lowers[dimension] <= uppers[dimension]
            
                print('\n',returns[maxindex])
            
            print('\n   uppers')
            values = np.arange(0,1+_epsilon,step)
            if len(values) > 0:
                returns = [_eval_dimchange(sim,lowers,uppers,dimension,\
                            min(lowers[dimension],u),u,horizon,runs) \
                            for u in values]
                maxindex = np.argmax(returns)
                u = values[maxindex]
                uppers[dimension] = weight*u + (1-weight)*uppers[dimension]
                lowers[dimension] = min(lowers[dimension],uppers[dimension])
                assert lowers[dimension] <= uppers[dimension]
            
                print('\n',returns[maxindex])

    print('Lowers', lowers)
    print('Uppers', uppers)

if __name__ == '__main__':
    
    #config = configuration.construct_martingale(np.arange(10), 3)
    config = configuration.construct_massdata(True)
    
    sim = inventory.Simulator(config)                
    optimize_independently(sim)