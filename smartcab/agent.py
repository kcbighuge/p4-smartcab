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

        ## Q table
        self.Q = {}  ## dict with states S as key, actions A as value

        ## actions A
        self.A = Environment.valid_actions  ## None, 'forward', 'left', 'right'

        ## total rewards
        self.reward_sum = 0

        ## epsilon for E-Greedy Exploration
        self.epsilon = 0.8

        ## keep track of transitions by step t
        self.transitions = {}

        ## keep track of n_trials
        self.current_trial = 0

        ## keep track of results
        self.results = []


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.reward_sum = 0
        self.current_trial += 1
        self.epsilon = max(0.95 - .2*(self.current_trial/4), .01)  ## decay epsilon, 100 trials
        self.transitions = {}
        self.init_deadline = self.env.get_deadline(self)


    def update(self, t):
        print '================'
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        print'next_waypoint: {}\n----'.format(self.next_waypoint)  ## [debug]
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        current_state = tuple(inputs.values() + [self.next_waypoint])

        # TODO: Select action according to your policy
        action = None

        ## create new Q(s,a) entry if not in dict
        if current_state not in self.Q.keys():
            self.Q[current_state] = [0, 0, 0, 0]

        ## assign max Q value for current state
        max_Q = self.Q[current_state].index(max(self.Q[current_state]))

        ## simulated annealing: take random action w/ probability epsilon
        ## generate random number to test if < epsilon
        if random.randint(1,100) <= (self.epsilon * 100):
            action = random.choice(self.A)
            print 'Step {}: Random Action!!'.format(t)
        else:
            action = self.A[max_Q]
            print 'Step {}: Optimal Action!!'.format(t)

        ## E-Greedy Exploration: decay epsilon
        if deadline > 5:
            self.epsilon = self.epsilon*.95
        else:
            self.epsilon = self.epsilon*.75
        print 'epsilon:', self.epsilon  ## [debug]

        ## Boltzmann exploration: P(a) = exp(Q(s,a) / sum(exp(Q)) / K), decay K over time

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        ## keep track sum of rewards
        self.reward_sum += reward
        print 'reward sum: {}'.format(self.reward_sum)  ## [debug]

        ## update history of states visited
        self.transitions[t] = (current_state, self.A.index(action), reward)
        print 'transition:', self.transitions[t]  ## [debug]

        ## Q-learning params
        gamma = 0.8  ## discount factor of next state/action Q value
        alpha = 0.2  ## learning rate, decay

        ## update Q table
        if self.Q[current_state] == [0,0,0,0]:
            self.Q[current_state] = [.5,.5,.5,.5]
            self.Q[current_state][self.A.index(action)] = 0
        if t!=0:
            self.Q[self.transitions[t-1][0]][self.transitions[t-1][1]] = \
                (1-alpha)*self.Q[self.transitions[t-1][0]][self.transitions[t-1][1]] + \
                (alpha * (self.transitions[t-1][2] + gamma * self.Q[current_state][max_Q]))
        if reward > 2:
            self.Q[current_state][self.A.index(action)] = \
                (1-alpha)*self.Q[current_state][self.A.index(action)] + \
                (alpha * reward)
            self.results.append(('Win!',self.init_deadline))  ## track wins
            print 'results:',self.results
        else:
            if deadline == 0:
                self.results.append(('Failed',self.init_deadline))  ## track fails
                print 'results:',self.results

        print "----\nQ({}): {}".format(len(self.Q), self.Q)  ## [debug]
        print "----\nLearningAgent.update({}): deadline = {}/{}, inputs = {}, action = {}, reward = {}".format(t, deadline, self.init_deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e)
    sim.run(n_trials=40)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
