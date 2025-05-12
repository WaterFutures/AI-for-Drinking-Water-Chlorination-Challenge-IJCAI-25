"""
Example of how to use the starter code.
"""
from env import WaterChlorinationEnv
from scenarios import load_scenario
from control_policy import ChlorinationControlPolicyRandom
from evaluation import evaluate


if __name__ == "__main__":
    # Create environment based on the first scenario
    # TODO: You might want to consider more than one scenario when training your policy/controller
    with WaterChlorinationEnv(**load_scenario(scenario_id=0)) as env:
        # Create new random policy
        # TODO: Develop a "smarter" policy/controller
        my_policy = ChlorinationControlPolicyRandom(env)

        # Evaluate policy
        r = evaluate(my_policy, env)
        print(r)
