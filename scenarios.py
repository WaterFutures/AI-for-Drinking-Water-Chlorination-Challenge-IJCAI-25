"""
This module contains the scenarios for the
"1st AI for Drinking Water Chlorination Challenge" @ IJCAI-2025.
"""
from epyt_flow.simulation import ScenarioSimulator, ScenarioConfig, EpanetConstants, ScadaData
from epyt_control.envs.actions import SpeciesInjectionAction
from epyt_flow.utils import download_if_necessary


def load_scenario(scenario_id: int, use_precomputed_hydraulics: bool = True) -> dict:
    """
    Creates and returns the scenario configurations which can be passed to the
    `WaterChlorinationEnv` class.

    Note that the first 10 scenarios (IDs 0 - 9) are 6 days long and
    the 11th scenario (ID 10) is 365 days long.

    Parameters
    ----------
    scenario_id : `int`
        ID of the scenario. Can range from 0 to 10.
    use_precomputed_hydraulics : `bool`, optional
        If True, pre-computed hydraulics will be used instead of first running a
        hydraulic simulation.

        Note that, if True, this function will first download the pre-computed
        hydraulics if those do not already exist in this folder.

        The default is True.

    Returns
    -------
    `dict`
        Arguments for instantiating the `WaterChlorinationEnv` class.
    """
    if not isinstance(scenario_id, int):
        raise TypeError("'scenario_id' must be an instance of 'int'")
    if scenario_id < 0 or scenario_id >= 11:
        raise ValueError(f"Invalid sceanrio ID '{scenario_id}'")

    use_zip = True
    if scenario_id <= 9:
        f_inp_in = f"CY-DBP_competition_stream_competition_6days_{scenario_id}.inp"
        f_msx_in = f"AI_challenge6days_{scenario_id}.msx"
        f_in_contamination_metadata = f"contamination_metadata_6days_{scenario_id}.mat"
        f_in_streams_data = f"Stream_demands_competition_6days_{scenario_id}.mat"
        f_hyd_file_in = f"CY-DBP_competition_stream_competition_6days_{scenario_id}.hyd"
        f_hyd_scada_in = f"CY-DBP_competition_stream_competition_6days_{scenario_id}_hyd.epytflow_scada_data"
    else:
        f_inp_in = "CY-DBP_competition_stream_competition_365days.inp"
        f_msx_in = "AI_challenge365days.msx"
        f_in_contamination_metadata = "contamination_metadata_365days.mat"
        f_in_streams_data = "Stream_demands_competition_365days.mat"
        f_hyd_file_in = "CY-DBP_competition_stream_competition_365days.hyd"
        f_hyd_scada_in = "CY-DBP_competition_stream_competition_365days_hyd.epytflow_scada_data"
        use_zip = False

    if use_precomputed_hydraulics is True:
        base_url = "https://filedn.com/lumBFq2P9S74PNoLPWtzxG4/IJCAI25-Challenge/"
        download_if_necessary(f_hyd_file_in, base_url + f_hyd_file_in, verbose=True)
        download_if_necessary(f_hyd_scada_in, base_url + f_hyd_scada_in, verbose=True)
    else:
        f_hyd_file_in = None
        f_hyd_scada_in = None

    # Load pre-computed hydraulics and remove everything except flows
    hyd_scada_in = None
    if f_hyd_scada_in is not None:
        hyd_scada_in = ScadaData.load_from_file(f_hyd_scada_in, use_zip=use_zip)
        hyd_scada_in = ScadaData(sensor_config=hyd_scada_in.sensor_config,
                                 sensor_readings_time=hyd_scada_in.sensor_readings_time,
                                 network_topo=hyd_scada_in.network_topo,
                                 warnings_code=hyd_scada_in.warnings_code,
                                 flow_data_raw=hyd_scada_in.flow_data_raw)

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
                                                    source_type_id=EpanetConstants.EN_MASS,
                                                    upper_bound=10000.)
                                                    for node_id, pat_id in zip(cl_injection_nodes,
                                                                               cl_injection_patterns)],
            "f_in_contamination_metadata": f_in_contamination_metadata,
            "f_in_streams_data": f_in_streams_data,
            "f_hyd_file_in": f_hyd_file_in,
            "hyd_scada_in": hyd_scada_in}
