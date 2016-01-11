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
        self.Q = [[0, 0, 0, 0]]  ## None, 'forward', 'left', 'right'

        ## initialize states
        ## state = [inputs, self.next_waypoint, deadline, self.reward_tot]
        self.S = [
                    [0,0,0],
                    [1,0,1],
                    [1,1,1],
                    [0,0,1]
        ]  ## forward_ok, left_ok, right_ok

        ## initialize actions
        self.A = Environment.valid_actions  ## None, 'forward', 'left', 'right'

        ## initialize rewards
        self.R = [
                    [0, -1, -1, -1],
                    [0, 1, -1, 1],
                    [0, 1, 1, 1],
                    [0, -1, -1, 1]
        ]  ## matrix of states S x action A

        ## initialize total rewards
        self.reward_tot = 0

        ## initialize epsilon for E-Greedy Exploration
        self.epsilon = .5


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.reward_tot = 0
        self.epsilon = .5


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        ##print 'state:', state

        # TODO: Select action according to your policy
        action = None

        ## auto-reset action
        action = self.next_waypoint
        self.next_waypoint = random.choice(Environment.valid_actions[:4])


        ## simulated annealing: probability epsilon will take random action
        if random.randint(1,100) < (self.epsilon * 100):
            self.next_waypoint = random.choice(Environment.valid_actions[:4])
        else:
            self.next_waypoint = random.choice(Environment.valid_actions[1:2])

        ## E-Greedy Exploration: decay epsilon
        self.epsilon = self.epsilon/2

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
        self.reward_tot += reward

        ###################################
        ## discount factor of next state/action Q value
        gamma = 0.5

        ## learning rate, decay
        alpha = 0.5

        #self.Qvalues[t] = reward + gamma * max(Qvalues[t+1])
        #self.Qvalues[t+1] = (1-alpha)*Qvalues[t] + alpha*Qvalues[t]
        ###################################

        print "\nLearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


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
