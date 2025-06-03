"""
This module contains a function for evaluating a given control policy on the evaluation metrics.
"""
import scipy
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
    sensor_config.bulk_species_node_sensors = {"CL2": all_junctions}
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

    # Infection risk
    msx_mat = scipy.io.loadmat(env._f_in_contamination_metadata)
    streams_mat = scipy.io.loadmat(env._f_in_streams_data)

    r_entero = 0.014472  # dose-response parameter for Enterovirus
    steps_per_day = 288

    People_per_node = np.round(streams_mat["People_per_node"]).flatten()
    Stream_faucet = streams_mat["Stream_faucet"] * 1000

    allJunctions = [str(n[0]) for n in msx_mat["dist_nodes"].flatten().tolist()]
    numJunctions = len(allJunctions)

    sensor_config = SensorConfig.create_empty_sensor_config(scada_data.sensor_config)
    sensor_config.bulk_species_node_sensors = {"P": allJunctions}
    scada_data.change_sensor_config(sensor_config)
    Pathogen_concentration = scada_data.get_data_bulk_species_node_concentration({"P": allJunctions})

    Total_Infections_day = None
    Total_risk_of_infection = None

    event_start = int(msx_mat["event_start"].flatten())
    aligned_start = max(1, event_start - 1) - 1  # Start one timestep before contamination
    aligned_end = min(aligned_start + steps_per_day - 1, Stream_faucet.shape[0]) + 1 # 288 steps total

    Stream_tap = np.round(Stream_faucet[aligned_start:aligned_end, :])
    cont_matrix = Pathogen_concentration[aligned_start - 3 * steps_per_day : aligned_end - 3 * steps_per_day, :] # We skipped the first three days

    stream_tot = np.sum(Stream_tap, axis=0)
    fraction = np.divide(People_per_node, stream_tot)
    Consumed_Stream = np.multiply(Stream_tap,  fraction)

    Volume = [None] * numJunctions
    for m in range(numJunctions):
        Volume[m] = np.zeros((Stream_tap.shape[0], int(People_per_node[m])))
        for n in range(int(People_per_node[m])):
            for t in range(Stream_tap.shape[0]):
                while Consumed_Stream[t, m] > 0:
                    if Consumed_Stream[t, m] < 0.00001:
                        break
                    if sum(Volume[m][:, n]) < 1:
                        delta = min([0.25, 1 - sum(Volume[m][:, n]), Consumed_Stream[t, m]])
                        Volume[m][t, n] = Volume[m][t, n] + delta
                        Consumed_Stream[t, m] = Consumed_Stream[t, m] - delta

                    n = n + 1
                    n = n % int(People_per_node[m])

    Dose = [None] * numJunctions
    Risk = [None] * numJunctions
    Total_risk_per_person = [None] * numJunctions
    Total_infections_ts = np.zeros((numJunctions, steps_per_day))

    for m in range(numJunctions):
        Dose[m] = np.multiply(Volume[m], cont_matrix[:, m].reshape(-1, 1))
        Risk[m] = 1. - np.exp(-r_entero * Dose[m])

        Total_risk_per_person[m] = [None for _ in range(int(People_per_node[m]))]
        for p in range(int(People_per_node[m])):
            Total_risk_per_person[m][p] = 1 - np.prod(1 - Risk[m][:, p])
        if np.all(Risk[m] == 0):
            continue

        cum_risk = np.zeros(Risk[m].shape)
        cum_risk[:, 0] = Risk[m][:, 0]
        for t in range(1, steps_per_day):
            for p in range(int(People_per_node[m])):
                cum_risk[t, p] = 1 - (1 - cum_risk[t - 1, p]) * (1 - Risk[m][t, p])
        Total_infections_ts[m, :] = np.sum(cum_risk, axis=1).T

    Total_Infections_day = np.sum([np.sum(item) for item in Total_risk_per_person])
    Total_risk_of_infection = (Total_Infections_day / np.sum(People_per_node)) * 100
    r["infection_risk"] = Total_risk_of_infection

    return r
