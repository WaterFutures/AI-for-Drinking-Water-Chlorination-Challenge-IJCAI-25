"""
Trains a simple PPO-based policy.
"""
from stable_baselines3 import PPO
from gymnasium.wrappers import NormalizeObservation

from env import WaterChlorinationEnv
from scenarios import load_scenario


if __name__ == "__main__":
    # Use PPO to train a MLP for mapping observations to actions
    #TODO: You might want to use more than one scenario when training the policy
    with WaterChlorinationEnv(**load_scenario(scenario_id=0)) as env:
        model = PPO("MlpPolicy", NormalizeObservation(env))
        model.learn(total_timesteps=100)
        model.save("my_ppo_model.zip")
