"""
This module contains a function for evaluating a given control policy on the evaluation metrics.
"""
import numpy as np
from epyt_flow.simulation import SensorConfig
from env import WaterChlorinationEnv
from control_policy import ChlorinationControlPolicy


def evaluate(policy: ChlorinationControlPolicy, env: WaterChlorinationEnv) -> dict:
    """
    Evaluates a given policy for controlling the chlorine injection pumps in a given environment.

    Parameters
    ----------
    policy : :class:`ChlorinationControlPolicy`
        Policy for controlling the chlorine injection pumps.
    env : :class:`WaterChlorinationEnv`
        Environment in which the policy is going to be evaluated.

    Returns
    -------
    `dict`
        All metrics.
    """
    if not isinstance(policy, ChlorinationControlPolicy):
        raise TypeError("'policy' must be an instance of 'ChlorinationControlPolicy' " +
                        f"but not of '{type(policy)}'")

    # Apply policy to environment
    scada_data = None
    actions = []

    obs, _ = env.reset()
    while True:
        action = policy(obs)
        actions.append(action)

        obs, _, terminated, _, info = env.step(action)
        if terminated is True:
            break

        current_scada_data = info["scada_data"]
        if scada_data is None:
            scada_data = current_scada_data
        else:
            scada_data.concatenate(current_scada_data)

    env.close()
    print("Done with simulation")

    # Evalute performance
    r = {}

    all_junctions = scada_data.network_topo.get_all_junctions()   # Only evaluate junctions but not tanks and reservoirs
    all_junctions.remove("distother_zones")
    all_junctions.remove("distother_dmas")
    all_junctions.remove("distTreatbefore")
    all_junctions.remove("distTreatafter")
    all_junctions.remove("distafterTank")

    sensor_config = SensorConfig.create_empty_sensor_config(scada_data.sensor_config)   # Change sensor config to contain all relevant information
    sensor_config.demand_sensors = all_junctions
    sensor_config.bulk_species_node_sensors = {"CL2": all_junctions,
                                               "P": all_junctions}
    scada_data.change_sensor_config(sensor_config)

    # Cost of control
    r["cost_control"] = np.sum(np.array(actions).flatten())

    # Chlorine concentration bounds
    upper_cl_bound = 0.4
    lower_cl_bound = 0.2

    bound_violations = 0
    nodes_quality = scada_data.get_data_bulk_species_node_concentration({"CL2": all_junctions})

    upper_bound_violation_idx = nodes_quality > upper_cl_bound
    bound_violations += np.sum(nodes_quality[upper_bound_violation_idx] - upper_cl_bound)

    lower_bound_violation_idx = nodes_quality < lower_cl_bound
    bound_violations += -1. * np.sum(nodes_quality[lower_bound_violation_idx] - lower_cl_bound)

    r["bound_violations"] = (1. / (len(all_junctions) * nodes_quality.shape[0])) * bound_violations

    # Fairness of chlorine concentration bound violations
    def score(x: float) -> float:
        if x > upper_cl_bound:
            return x - upper_cl_bound
        elif x < lower_cl_bound:
            return lower_cl_bound - x
        else:
            return 0.

    nodes_quality_scores = np.vectorize(score)(nodes_quality)
    avg_node_viol = np.mean(nodes_quality_scores, axis=0)

    r["bound_violations_fairness"] = max(avg_node_viol) - min(avg_node_viol)

    # Smoothness of chlorine injection
    s = []
    for t in range(len(actions) - 1):
        s.append(np.abs(actions[t] - actions[t+1]))
    s = np.mean(s, axis=0)

    r["injection_control_score"] = max(s)

    return r
