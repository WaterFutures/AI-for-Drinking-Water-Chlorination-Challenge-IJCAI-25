"""
This module contains the water chlorination control environment that is to be used in the
"1st AI for Drinking Water Chlorination Challenge" @ IJCAI-2025.
"""
from typing import Optional, Any
import numpy as np
from epyt_control.envs import EpanetMsxControlEnv
from epyt_control.envs.actions import SpeciesInjectionAction
from epyt_flow.simulation import ScadaData, SensorConfig, ScenarioConfig
from epyt_flow.utils import to_seconds


class WaterChlorinationEnv(EpanetMsxControlEnv):
    """
    Control environment.
    """
    def __init__(self, scenario_config: ScenarioConfig, f_in_contamination_metadata: str,
                 f_in_streams_data: str, action_space: list[SpeciesInjectionAction],
                 f_hyd_file_in: str = None, hyd_scada_in: ScadaData = None):
        super().__init__(scenario_config=scenario_config,
                         action_space=action_space,
                         rerun_hydraulics_when_reset=False,
                         hyd_file_in=f_hyd_file_in, hyd_scada_in=hyd_scada_in,
                         reload_scenario_when_reset=False)

        self.__sensor_config_reward = None
        self._f_in_contamination_metadata = f_in_contamination_metadata
        self._f_in_streams_data = f_in_streams_data

    def reset(self, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None
              ) -> tuple[np.ndarray, dict]:
        # Reset
        super().reset(seed, options)

        # Set constant chlorine injection
        #self._scenario_sim.epanet_api.setMSXPattern("CL2PAT", [3000])
        self._scenario_sim.epanet_api.setMSXPattern("CL2PAT1", [500])
        self._scenario_sim.epanet_api.setMSXPattern("CL2PAT2", [10])
        self._scenario_sim.epanet_api.setMSXPattern("CL2PAT3", [10])
        self._scenario_sim.epanet_api.setMSXPattern("CL2PAT4", [10])
        self._scenario_sim.epanet_api.setMSXPattern("CL2PAT5", [10])

        # Skip first three days to give the network time to settle a proper initial state
        time_step = self._scenario_sim.epanet_api.getTimeHydraulicStep()
        n_steps_to_skip = int(to_seconds(days=3) / time_step)

        current_scada_data = None
        for _ in range(n_steps_to_skip):
            current_scada_data, _ = self._next_sim_itr()

        obs = self._get_observation(current_scada_data)

        return obs, {"scada_data": current_scada_data}

    def _compute_reward_function(self, scada_data: ScadaData) -> float:
        """
        Computes the current reward based on the current sensors readings (i.e. SCADA data).
        Sums up (negative) residuals for out of bounds Cl concentrations at nodes -- i.e.
        reward of zero means everythings is okay, while a negative reward denotes Cl concentration
        bound violations
        TODO: Override this method with a "better" reward function!

        Parameters
        ----------
        :class:`epyt_flow.simulation.ScadaData`
            Current sensor readings.

        Returns
        -------
        `float`
            Current reward.
        """
        # TODO: Replace with smth. more reasonable!
        # Sum up (negative) residuals for out of bounds Cl concentrations at nodes -- i.e.
        # reward of zero means everythings is okay, while a negative reward
        # denotes Cl concentration bound violations
        reward = 0.

        # Regulation Limits (taken from the evaluation metrics)
        upper_cl_bound = .4  # (mg/l)
        lower_cl_bound = .2  # (mg/l)

        if self.__sensor_config_reward is None:
            self.__sensor_config_reward = SensorConfig.create_empty_sensor_config(scada_data.sensor_config)
            self.__sensor_config_reward.bulk_species_node_sensors = {"CL2": scada_data.sensor_config.nodes}
        scada_data.change_sensor_config(self.__sensor_config_reward)

        nodes_quality = scada_data.get_data_bulk_species_node_concentration({"CL2": scada_data.sensor_config.nodes})

        upper_bound_violation_idx = nodes_quality > upper_cl_bound
        reward += -1. * np.sum(nodes_quality[upper_bound_violation_idx] - upper_cl_bound)

        lower_bound_violation_idx = nodes_quality < lower_cl_bound
        reward += np.sum(nodes_quality[lower_bound_violation_idx] - lower_cl_bound)

        return reward
