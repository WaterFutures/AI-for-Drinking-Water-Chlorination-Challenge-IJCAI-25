"""
Note that every submission must contains a file "load_my_policy.py" which contains a function
load_policy(env: WaterChlorinationEnv) -> ChlorinationControlPolicy for loading and returning the final policy/controller.
"""
from env import WaterChlorinationEnv
from control_policy import ChlorinationControlPolicy

from my_policy import MyPolicy

def load_policy(env: WaterChlorinationEnv) -> ChlorinationControlPolicy:
    # Create and load our final policy/controlelr
    my_policy = MyPolicy(env)
    my_policy.load_from_file("my_ppo_model.zip")

    return my_policy
