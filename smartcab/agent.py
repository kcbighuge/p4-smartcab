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
        self.Q = {}

        ## actions A
        self.A = Environment.valid_actions  ## None, 'forward', 'left', 'right'
        ##self.A = ['forward', 'left', 'right', None]

        ## keep track of total rewards earned
        self.reward_sum = 0

        ## epsilon for E-Greedy Exploration
        self.epsilon = 0.5

        ## keep track of transitions by step t
        self.transitions = {}

        ## keep track of n_trials
        self.current_trial = 0

        ## keep track of results as tuples of (Win or Failed, initial deadline)
        self.results = []

        ## keep track of optimal policy used as tuples of (optimal moves, # of moves)
        self.optimal_policy_used = []


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

        ## reset variables
        self.reward_sum = 0
        self.transitions = {}

        ## keep track of initial deadline for the trial
        self.init_deadline = self.env.get_deadline(self)

        ## keep track of optimal move during update, 1 = yes, 0 = no
        self.optimal_action_used = []

        ## increment trial counter
        self.current_trial += 1

        ## E-Greedy Exploration: decay epsilon, goes to 0 at 40th of 50 trials
        self.epsilon -= .025*(self.current_trial/2)


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state

        ## create state as inputs, next_waypoint
        current_state = tuple(inputs.values() + [self.next_waypoint])
        ##current_state = tuple(inputs.values())  ## dont incl next_waypoint

        # TODO: Select action according to your policy
        action = None

        ## create new Q(s,a) entry if not in dict
        if current_state not in self.Q.keys():
            ##self.Q[current_state] = [0, 0, 0, 0]  ## initialize w/ zeros
            self.Q[current_state] = [3, 3, 3, 3]  ## initialize non-zero

        ## assign max Q value for current state
        max_Q = self.Q[current_state].index(max(self.Q[current_state]))

        ## simulated annealing: take random action w/ probability epsilon
        ''' generate random number to choose random action
        if random.randint(1,100) <= (self.epsilon * 100):
            action = random.choice(self.A)
            print 'Step {}: Random Action!!'.format(t)  ## [debug]
        else:
            action = self.A[max_Q]
            print 'Step {}: Max Q Action!!'.format(t)  ## [debug]'''

        ## E-Greedy Exploration: decay epsilon with each step in trial
        self.epsilon = self.epsilon*.9
        ##print 'epsilon:', self.epsilon  ## [debug]

        ## assign action randomly or based on max Q value
        ##action = random.choice(self.A)
        action = self.A[max_Q]

        #####################################
        ## keep track of optimal policy
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
        #####################################

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        ## increment sum of rewards
        self.reward_sum += reward
        ##print 'reward sum: {}'.format(self.reward_sum)  ## [debug]
        ##print 'next waypoint: %s' % self.next_waypoint  ## [debug]

        ## update history of states visited
        self.transitions[t] = (current_state, self.A.index(action), reward)
        print 'transition:', self.transitions[t]  ## [debug]

        ## Q-learning params
        gamma = 0.5  ## discount factor of max Q(s',a')
        alpha = 0.2  ## learning rate, decay Q value

        ## update Q table
        if t!=0:  ## update after first step
            self.Q[self.transitions[t-1][0]][self.transitions[t-1][1]] = \
                (1-alpha)*self.Q[self.transitions[t-1][0]][self.transitions[t-1][1]] + \
                (alpha * (self.transitions[t-1][2] + gamma * self.Q[current_state][max_Q]))

        ## update Q, results at end of trial
        if reward > 2:  ## if destination reached
            self.Q[current_state][self.A.index(action)] = \
                (1-alpha)*self.Q[current_state][self.A.index(action)] + \
                (alpha * reward)

            self.results.append(('Win!',self.init_deadline))  ## track wins
            print 'results:',self.results

            self.optimal_policy_used.append((sum(self.optimal_action_used), len(self.optimal_action_used)))  ## track optimal policy moves
            print 'optimal policy used: {}'.format(self.optimal_policy_used)

        else:  ## if destination not reached
            if deadline == 0:
                self.Q[current_state][self.A.index(action)] = \
                    (1-alpha)*self.Q[current_state][self.A.index(action)] + \
                    (alpha * reward)

                self.results.append(('Failed',self.init_deadline))  ## track fails
                print 'results:',self.results

        print "Q({}): {}".format(len(self.Q), self.Q)  ## [debug]
        print "LearningAgent.update({}): deadline = {}/{}, inputs = {}, action = {}, reward = {}".format(t, deadline, self.init_deadline, inputs, action, reward)  # [debug]
        print "============"


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e)
    sim.run(n_trials=20)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
