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


    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state


        # TODO: Select action according to your policy
        action = None

        ###################################
        # Test primary agent acting randomly
        action_okay = True
        if self.next_waypoint == 'right':
            if inputs['light'] == 'red' and inputs['left'] == 'forward':
                action_okay = False
        elif self.next_waypoint == 'straight':
            if inputs['light'] == 'red':
                action_okay = False
        elif self.next_waypoint == 'left':
            if inputs['light'] == 'red' or (inputs['oncoming'] == 'forward' or inputs['oncoming'] == 'right'):
                action_okay = False

        if action_okay:
            action = self.next_waypoint
            self.next_waypoint = random.choice(Environment.valid_actions[1:3])
        ###################################

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        # Q(s,a) = R(s) + γ ∑ T(s,a,s') max_a' Q(s',a')
        # Q_hat(s,a) <-α r + γ max_a' Q_hat(s',a')
        # U(s) = r + γ max_a' Q_hat(s',a')
        Q_hat[t] = (1-alpha)*Q_hat[t] + (alpha* (reward + gamma * max(Q_hat[t+1])))
        U(t) = reward + gamma * max(Q_hat[t+1])
        ###################################

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=False)  # set agent to track

    # Now simulate it
    sim = Simulator(e)
    sim.run(n_trials=5)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
