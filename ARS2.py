"""
ARS Algorithm
"""

import numpy as np
from Knot_Environment2 import Environment
from matplotlib import pyplot as plt
# Setting Hyperparameters

class Hp():
    
    def __init__(self):
        self.nb_steps = 30
        self.episode_length = 10
        self.learning_rate = 0.02
        self.nb_directions = 15
        self.nb_best_directions = 10
        assert self.nb_best_directions <= self.nb_directions
        self.noise = 0.7
        self.seed = 1
        self.theta_lb = -2
        self.theta_ub = 2
        self.BIAS = self.nb_steps
        self.env_name = "Knot Land"
        
hp = Hp()
        
# Normalizing States
# Don't think we need to use this for this application, but nice to have
        
class Normalizer():
    
    def __init__(self, nb_inputs):
        self.n = np.zeros(nb_inputs)
        self.mean = np.zeros(nb_inputs)
        self.mean_diff = np.zeros(nb_inputs)
        self.var = np.zeros(nb_inputs)
        
    def observe(self, x):
        self.n += 1.
        last_mean = self.mean.copy()
        self.mean = (x - self.mean) / self.n
        self.mean_diff = (x - last_mean) * (x - self.mean)
        self.var = (self.mean_diff / self.n).clip(min = 1e-2)
        
    def normalize(self, inputs):
        obs_mean = self.mean
        obs_std = np.sqrt(self.var)
        return (inputs - obs_mean) / obs_std
    
# Build the AI
        
class Policy():
    
    def __init__(self, max_crossings): # Alter this if I change the application
        input_size = 2*max_crossings
        output_size = 5
        self.theta = np.random.random((output_size, input_size))                        # Matrix of weights
        
    def evaluate(self, input, delta = None, direction = None):
        # print(self.theta.shape, input.shape)
        
        if direction is None:
            # print("Theta:", self.theta, "Input", input)
            return self.theta@input
        elif direction == "positive":
            return (self.theta + hp.noise*delta)@input                          # Positive finite difference
        else:
            return (self.theta - hp.noise*delta)@input                          # Negative finite difference 
     
    # Gets dimensions of our theta
    def sample_deltas(self):
        return [np.random.randn(*self.theta.shape) for _ in range(hp.nb_directions)]   

    def update(self, rollouts, sigma_r):
        step = np.zeros(self.theta.shape)
#        print("Step:", step)
#        print("Rollouts:", rollouts)
        for r_pos, r_neg, d in rollouts:
            # print(r_pos, r_neg, d)
            step += (r_pos - r_neg) * d
        # print(sigma_r, "Step:", step)
        self.theta += hp.learning_rate / (hp.nb_best_directions * sigma_r) * step # Updates the matrix
        self.theta.clip(min = hp.theta_lb, max = hp.theta_ub)

# Exploring the policy on one specific direction and over one episode

#def explore(env, policy, normalizer = None, direction = None, delta = None, show_gauss = False):
#
#    num_plays = 0
#    env.reset()
#    state = env.knotToMatrix()
#    overall_reward = 0
#    done = False
#    curr_max = -1000
#    
#    while not done and num_plays < hp.episode_length:
#        
#        action = policy.evaluate(state, delta, direction)
#        sigmoid_action = 1 / (1 + np.exp(-action)) # Run our result matrix through the sigmoid activation function
#        state, local_reward, done = env.step(sigmoid_action.T) # Use the transpose so we get a 2n x 5 matrix instead of 5 x 2n
#        overall_reward += local_reward
#        if local_reward > curr_max:
#            curr_max = local_reward
#        num_plays += 1
#        if show_gauss:
#            print(env.curr.gauss_code)
#    # print(overall_reward, curr_max*hp.BIAS)
#    return overall_reward / num_plays

def explore(env, policy, normalizer = None, direction = None, delta = None, show_gauss = False, overall_max = -1000):

    num_plays = 0
    env.reset()
    state = env.knotToMatrix()
    overall_reward = 0
    done = False
    curr_max = -1000
    
    while not done and num_plays < hp.episode_length:
        
        action = policy.evaluate(state, delta, direction)
        sigmoid_action = 1 / (1 + np.exp(-action)) # Run our result matrix through the sigmoid activation function
        state, local_reward, done = env.step(sigmoid_action.T) # Use the transpose so we get a 2n x 5 matrix instead of 5 x 2n
        if local_reward > curr_max:
            curr_max = local_reward
        num_plays += 1
    overall_reward = curr_max
    # print(overall_reward, curr_max*hp.BIAS)
    if overall_reward > overall_max:
        overall_max = overall_reward
    else:
        overall_reward -= overall_max
    return overall_reward, overall_max

# Training the AI

def train(env, policy, normalizer = None):
    rewards = list()
    thetas = list()
    i = 0
    for step in range(hp.nb_steps):
        
        # Initializing the perturbations deltas and the positive/negative rewards
        deltas = policy.sample_deltas() # Gets delta matricies
        positive_rewards = [0] * hp.nb_directions
        negative_rewards = [0] * hp.nb_directions # Not rewards below zero. Opposite rewards
        
        env.reset()
        o_max = -1000
        # Getting the positive rewards in positive directions
        for k in range(hp.nb_directions):
            positive_rewards[k], o_max = explore(env, policy, normalizer, direction = "positive", delta = deltas[k], overall_max = o_max)
            print(o_max)
            # print("Positive direction", k, "complete for step", step)
            
        # Getting the negative rewards in the negative/opposite directions
        o_max = -1000
        for k in range(hp.nb_directions):
            negative_rewards[k], o_max = explore(env, policy, normalizer, direction = "negative", delta = deltas[k], overall_max = o_max)
            print(o_max)
            # print("Negative direction", k, "complete for step", step)
            
        # Gathering all the positive/negative rewards to compute the standard deviation of these rewards
        all_rewards = np.array(positive_rewards + negative_rewards)
#        print("All Rewards:", all_rewards)
        sigma_r = all_rewards.std().clip(min = 1e-2) # Gets the standard deviation of rewards
        
        # Sorting the directions by the maximum of rewards
        print("Getting scores...")
        scores = {k: max(r_pos, r_neg) for k, (r_pos, r_neg) in enumerate(zip(positive_rewards, negative_rewards))}
        order = sorted(scores.keys(), key = lambda x:scores[x])[:hp.nb_best_directions] # Sort by the values and get the keys
        rollouts = [(positive_rewards[k], negative_rewards[k], deltas[k]) for k in order]
        
        # Updating our policy
        # print(policy.theta)
        print("Updating policy...")
        policy.update(rollouts, sigma_r)
        thetas.append(np.copy(policy.theta))
        # print(policy.theta)
        # Printing the final reward of the policy after the update
        print("Evaluating rewards...")
        reward_evaluation, _ = explore(env, policy, normalizer)
        print("Step: ", step, "Reward: ", reward_evaluation)
        rewards.append(reward_evaluation)
        i+=1
        
    return rewards, thetas
        
def load(infile):
    with open(infile, "r") as fs:
        j = 0
        lines = list()
        line = fs.readline()
        while line:
            lines.append([int(i) for i in line.split(",")])
            if j % 100 == 0:
                print(j)
            j+=1
            line = fs.readline()
    return lines
    
        
def evaluate(env, policy):
    reward = explore(env, policy, normalizer=None, show_gauss=False)
    return reward
        
      
if __name__ == '__main__':
    MAX_CROSSINGS = 10
    hard_unknot = [1,-2,3,-4,-5,6,-7,8,9,-1,2,-3,4,-9,-6,7,-8,5,1,1,1,1,-1,-1,-1,-1,1]
    manu_trefoil = [2, 1, 6, 4, -4, -6, -5, -2, 3, 5, -1, -3, 1, 1, 1, 1, 1, -1]
    # env = Environment([1,2,3,-1,-2,-3,1,-1,1], max_crossings = MAX_CROSSINGS, standardize=False)
    # env = Environment([1,-2,2,-3,3,-4,4,-5,5,-6,6,-1,1,1,1,1,1,1], max_crossings = MAX_CROSSINGS, standardize=False)
    codes = load("FormattedCodes.txt")
    env = Environment(manu_trefoil, max_crossings = MAX_CROSSINGS, standardize=True)
    policy3 = Policy(MAX_CROSSINGS)
    
    rewards, thetas = train(env, policy3)
    plt.plot(np.arange(1,hp.nb_steps+1), rewards)
    plt.title("Rewards over time for 6 crossing knot")
    plt.ylabel("Reward")
    plt.xlabel("Step Number")
    
    explore(env, policy3, show_gauss = True)

#    for i in range(1):
#        print("Knot #", i)
#        # env.setKnot(knot=hard_unknot)
#        rewards, thetas = train(env, policy3)
#    #    t = np.array(thetas)
        
#        
##    np.save("theta_13122.npy", np.array(thetas))
##    
    
##    name = "hard_unknot_for_{0}_{1}_{2}_{3}.jpeg".format(hp.learning_rate,hp.noise,hp.nb_best_directions,hp.nb_directions)
#    
#    # plt.savefig(name)
#    # assert not np.allclose(policy1.theta, start)
#        
#    print("After")

    
    
       
        
    
        
    
                            