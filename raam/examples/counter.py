"""
=================================================
Simple test simulator (raam.examples.counter)
=================================================

Counts up and down with the actions
"""
import random
import itertools
import raam

class Counter(raam.simulator.Simulator):  
    """
    Decision state: position in chain
    Expectation state: position in chain, change (+1,-1)
    Initial (decision) state: 0
    Actions: {plus, minus}
    Rewards: succ_prob%: next position, 1-succ_prob% this position in chain
    """
    def __init__(self,succ_prob=0.9):
        self.succ_prob = succ_prob

    @property
    def discount(self):
        return 0.9
        
    def transition_dec(self,decstate,action):
        if action == 'plus':
            return (decstate, +1)
        elif action == 'minus':
            return (decstate, -1)
        else:
            raise ValueError('Invalid action')
        
    def transition_exp(self,expstate):
        pos,act = expstate
        if random.random() <= self.succ_prob:
            return pos,pos + act
        else:
            return pos,pos
            
    def end_condition(self,decstate):
        return False
        
    def initstates(self):
        return itertools.cycle([0])
        
    def actions(self,decstate):
        return ['plus','minus']


class StatefulCounter(raam.simulator.StatefulSimulator):  
    """
    Decision state: position in chain
    Expectation state: position in chain, change (+1,-1)
    Initial (decision) state: 0
    Actions: {plus, minus}
    Rewards: succ_prob%: next position, 1-succ_prob% this position in chain
    """

    def __init__(self, succ_prob=0.9):
        self.state = None
        self.succ_prob = succ_prob

    @property
    def discount(self):
        return 0.9
        
    def transition_dec(self,action):
        decstate = self.state
        
        if action == 'plus':
            self.state = (decstate, +1)
        elif action == 'minus':
            self.state = (decstate, -1)
        else:
            raise ValueError('Invalid action')
        
        return self.state
        
    def transition_exp(self):        
        pos,act = self.state

        if random.random() <= self.succ_prob:
            self.state = pos + act
        else:
            self.state = pos            
        return pos,self.state            
            
    def end_condition(self,decstate):
        return False
        
    def reinitstate(self,param):
        self.state = 0
        return self.state
        
    def actions(self):
        return ['plus','minus']
