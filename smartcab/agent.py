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
        # TODO: Initialize any additional variables here
        self.Q = [
            [0, 0, 0, 0], [0, 0, 0, 0],
            [0, 0, 0, 0], [0, 0, 0, 0],
            [0, 0, 0, 0], [0, 0, 0, 0],
            [0, 0, 0, 0], [0, 0, 0, 0]
            ]  ## None, 'forward', 'left', 'right'

        ## states S
        self.S = [
            (0,0,0, True), (0,0,0, False),
            (1,0,1, True), (1,0,1, False),
            (1,1,1, True), (1,1,1, False),
            (0,0,1, True), (0,0,1, False)
            ]  ## forward_ok, left_ok, right_ok, done??

        ## actions A
        self.A = Environment.valid_actions  ## None, 'forward', 'left', 'right'

        ## rewards R
        self.R = [
            [10, -1, -1, -1], [0, -1, -1, -1],
            [10,  1, -1,  1], [0,  1, -1,  1],
            [10,  1,  1,  1], [0,  1,  1,  1],
            [10, -1, -1,  1], [0, -1, -1,  1]
            ]  ## matrix of states S x action A

        ## total rewards
        self.reward_sum = 0

        ## epsilon for E-Greedy Exploration
        self.epsilon = .8

        ## keep track of states by step t
        self.state_history = {}


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.reward_sum = 0
        self.epsilon = .8
        self.state_history = {}


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        if inputs['light'] == 'red' and inputs['left'] == 'forward':
            current_state = 1  ## only None allowed
        elif inputs['light'] == 'red' and inputs['left'] != 'forward':
            current_state = 7  ## only right allowed
        elif inputs['light'] == 'green' and (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
            current_state = 3  ## forward, right allowed
        elif inputs['light'] == 'green' and not (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
            current_state = 5  ## any allowed

        # TODO: Select action according to your policy
        action = None

        ## simulated annealing: take random action w/ probability epsilon
        print '----------------------------'

        ## assign max Q value for current state
        max_Q = self.Q[current_state].index(max(self.Q[current_state]))

        ## generate random number to test if < epsilon
        if random.randint(1,100) < (self.epsilon * 100):
            action = random.choice(self.A)
            print 'Step {}: Random Action!!'.format(t)
        else:
            action = self.A[max_Q]
            print 'Step {}: Optimal Action!!'.format(t)

        self.state_history[t] = [current_state, self.A.index(action)]

        ## E-Greedy Exploration: decay epsilon
        self.epsilon = self.epsilon*.99
        print 'epsilon:', self.epsilon  ## [debug]

        ###################################
        ## Test primary agent acting randomly
        '''
        action_okay = True

        if self.next_waypoint == 'right':
            if inputs['light'] == 'red' and inputs['left'] == 'forward':
                action_okay = False
        elif self.next_waypoint == 'forward':
            if inputs['light'] == 'red':
                action_okay = False
        elif self.next_waypoint == 'left':
            if inputs['light'] == 'red' or (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
                action_okay = False

        if action_okay:
            action = self.next_waypoint
            self.next_waypoint = random.choice(Environment.valid_actions[:4])
        '''
        ###################################

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        self.reward_sum += reward  ## keep track sum of rewards
        print 'reward sum: {}'.format(self.reward_sum)  ## [debug]

        ## Q-learning params
        gamma = 0.9  ## discount factor of next state/action Q value
        alpha = 0.2  ## learning rate, decay

        ## update Q table
        if t == 0:
            self.Q[current_state][self.A.index(action)] = reward
        else:
            self.Q[self.state_history[t-1][0]][self.state_history[t-1][1]] = \
                (1-alpha)*self.Q[self.state_history[t-1][0]][self.state_history[t-1][1]] + \
                (alpha * (reward + gamma * self.Q[current_state][max_Q]))
        print 'Q: {}'.format(self.Q)  ## [debug]

        print "\nLearningAgent.update({}): deadline = {}, inputs = {}, action = {}, reward = {}".format(t, deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e)
    sim.run(n_trials=5)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
