import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'blue'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # DONE: Initialize any additional variables here

        ## actions A
        self.A = Environment.valid_actions  ## None, 'forward', 'left', 'right'

        ## Q table: state = (light, oncoming, next_waypoint)
        self.Q = {}
        for i in ['green', 'red']:  ## loop thru possible lights
            for j in ['oncoming','no_oncoming']:  ## oncoming traffic or not
                for k in self.A:  ## loop through next_waypoints
                    self.Q[(i,j,k)] = [3] * len(self.A)  ## init Q(s,a)

        ''' Extra variables for alternate implementations
        ## keep track of total rewards earned
        self.reward_sum = 0

        ## epsilon for E-Greedy Exploration
        self.epsilon = 0.5

        ## keep track of n_trials
        self.current_trial = 0

        ## keep track of results as tuples of (Win or Failed, initial deadline)
        self.results = []

        ## keep track of optimal policy used as tuples of (optimal moves, # of moves)
        self.optimal_policy_used = []
        '''


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # DONE: Prepare for a new trip; reset any variables here, if required

        ''' Extra variables for alternate implementations
        self.reward_sum = 0  ## reset within-trial reward total
        ## keep track of initial deadline for the trial
        self.init_deadline = self.env.get_deadline(self)

        ## keep track of optimal move during update, 1 = yes, 0 = no
        self.optimal_action_used = []

        ## increment trial counter
        self.current_trial += 1

        ## E-Greedy Exploration: decay epsilon, goes to 0 at 40th of 50 trials
        self.epsilon -= .025*(self.current_trial/2)
        '''

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # DONE: Update state

        ## update state as (light, oncoming, next_waypoint)
        traffic = ('no_oncoming' if inputs['oncoming'] == None else 'oncoming')
        self.state = (inputs.values()[0], traffic, self.next_waypoint)
        ##print 'current state:', self.state  ## [debug]

        # DONE: Select action according to your policy
        action = None

        ## assign max Q value for current state
        max_Q = self.Q[self.state].index(max(self.Q[self.state]))

        ## assign action based on max Q value
        action = self.A[max_Q]
        
        ## 3 alternate methods explored
        ''' 1. simulated annealing: take random action w/ probability epsilon
        ## generate random number to choose random action
        if random.randint(1,100) <= (self.epsilon * 100):
            action = random.choice(self.A)
            print 'Step {}: Random Action!!'.format(t)  ## [debug]
        else:
            action = self.A[max_Q]
            print 'Step {}: Max Q Action!!'.format(t)  ## [debug]
        '''

        ''' 2. E-Greedy Exploration: decay epsilon with each step in trial
        self.epsilon = self.epsilon*.9
        print 'epsilon:', self.epsilon  ## [debug]
        '''

        ''' 3. assign action randomly
        action = random.choice(self.A)
        '''
        
        ''' Keeping track of optimal policy
        ## assumes next_waypoint is ideal (best) action at each step
        best_action_ok = True
        if self.next_waypoint == 'right':
            if inputs['light'] == 'red' and inputs['left'] == 'forward':
                best_action_ok = False
        elif self.next_waypoint == 'forward':
            if inputs['light'] == 'red':
                best_action_ok = False
        elif self.next_waypoint == 'left':
            if inputs['light'] == 'red' or (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
                best_action_ok = False

        best_action = None
        if best_action_ok:
            best_action = self.next_waypoint

        if best_action == action:
            self.optimal_action_used.append(1)  ## optimal action
        else:
            self.optimal_action_used.append(0)  ## not optimal action
        '''

        # Execute action and get reward
        reward = self.env.act(self, action)

        ''' Keep track of total rewards
        ## increment sum of rewards
        self.reward_sum += reward
        print 'Reward sum: {}'.format(self.reward_sum)  ## [debug]
        '''

        # DONE: Learn policy based on state, action, reward
        ## Q-learning params
        gamma = 0.5  ## discount factor of max Q(s',a')
        alpha = 0.2  ## learning rate, decay Q value

        ## grab next state for Q(s',a')
        next_inputs = self.env.sense(self)
        next_traffic = ('no_oncoming' if next_inputs['oncoming'] == None else 'oncoming')
        next_next_waypoint = self.planner.next_waypoint()
        next_state = (next_inputs.values()[0], next_traffic, next_next_waypoint)
        ##print 'next_state:', next_state  ## [debug]

        ## update Q table
        self.Q[self.state][self.A.index(action)] = \
            (1-alpha)*self.Q[self.state][self.A.index(action)] + \
            (alpha * (reward + gamma * max(self.Q[next_state])))
        ##print 'Q({}): {}'.format(len(self.Q), self.Q)  ## [debug]

        print 'LearningAgent.update({}): deadline = {}, inputs = {}, action = {}, reward = {}'.format(t, deadline, inputs, action, reward)  # [debug]

        ''' Update list of results at end of trial
        if self.env.done == True:  ## if destination reached
            self.results.append(('Win!',self.init_deadline))  ## track wins
            print '---- Results:',self.results  ## [debug]

            self.optimal_policy_used.append((sum(self.optimal_action_used), len(self.optimal_action_used)))  ## track optimal policy moves
            print '---- Optimal moves: {}'.format(self.optimal_policy_used)  ## [debug]

        elif deadline==0:  ## if destination not reached
            self.results.append(('Failed',self.init_deadline))  ## track fails
            print '---- Results:',self.results  ## [debug]
        '''


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e)
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
