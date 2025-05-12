"""
This module contains the scenarios for the
"1st AI for Drinking Water Chlorination Challenge" @ IJCAI-2025.
"""
from epyt_flow.simulation import ScenarioSimulator, ScenarioConfig, ToolkitConstants
from epyt_control.envs.actions import SpeciesInjectionAction


def load_scenario(scenario_id: int) -> dict:
    """
    Creates and returns the scenario configurations which can be passed to the
    `WaterChlorinationEnv` class.

    Parameters
    ----------
    scenario_id : `int`
        ID of the scenario. Can range from 0 to 3.

    Returns
    -------
    `dict`
        Arguments for instantiating the `WaterChlorinationEnv` class.
    """
    if not isinstance(scenario_id, int):
        raise TypeError("'scenario_id' must be an instance of 'int'")
    if scenario_id < 0 or scenario_id >= 3:
        raise ValueError(f"Invalid sceanrio ID '{scenario_id}'")

    f_inp_in = f"CY-DBP_competition_stream_competition_6days_{scenario_id}.inp"
    f_msx_in = f"AI_challenge6days_{scenario_id}.msx"
    f_in_contamination_metadata = f"contamination_metadata_6days_{scenario_id}.mat"

    sensor_config = None
    with ScenarioSimulator(f_inp_in=f_inp_in, f_msx_in=f_msx_in) as scenario:
        scenario.set_flow_sensors(["5", "p-1144"])
        scenario.set_bulk_species_node_sensors({"CL2": ["dist423", "dist225", "dist989", "dist1283", "dist1931",
                                                        "dist342", "dist275", "dist354", "dist885", "dist485",
                                                        "dist631", "dist1332", "dist1607", "dist1459", "dist1702",
                                                        "dist1975", "dist1903"]})

        sensor_config = scenario.sensor_config

    cl_injection_nodes = ["dist423", "dist225", "dist989", "dist1283", "dist1931"]
    cl_injection_patterns = ["CL2PAT1", "CL2PAT2", "CL2PAT3", "CL2PAT4", "CL2PAT5"]
    return {"scenario_config": ScenarioConfig(f_inp_in=f_inp_in, f_msx_in=f_msx_in,
                                              sensor_config=sensor_config),
            "action_space": [SpeciesInjectionAction(species_id="CL2", node_id=node_id,
                                                    pattern_id=pat_id,
                                                    source_type_id=ToolkitConstants.EN_MASS,
                                                    upper_bound=10000.)
                                                    for node_id, pat_id in zip(cl_injection_nodes,
                                                                               cl_injection_patterns)],
            "f_in_contamination_metadata": f_in_contamination_metadata}
