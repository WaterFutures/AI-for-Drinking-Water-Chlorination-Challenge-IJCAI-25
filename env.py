"""
This module contains the water chlorination control environment that is to be used in the
"1st AI for Drinking Water Chlorination Challenge" @ IJCAI-2025.
"""
from typing import Optional, Any, Union
from copy import deepcopy
import numpy as np
from epyt_control.envs import EpanetMsxControlEnv
from epyt_control.envs.actions import SpeciesInjectionAction
from epyt_flow.simulation import ScadaData, SensorConfig, ScenarioConfig, EpanetConstants
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
        def setMSXPattern(pat_id, pat):
            pattern_idx = self._scenario_sim.epanet_api.MSXgetindex(EpanetConstants.MSX_PATTERN, pat_id)
            self._scenario_sim.epanet_api.MSXsetpattern(pattern_idx, pat, len(pat))

        setMSXPattern("CL2PAT1", [500])
        setMSXPattern("CL2PAT2", [10])
        setMSXPattern("CL2PAT3", [10])
        setMSXPattern("CL2PAT4", [10])
        setMSXPattern("CL2PAT5", [10])

        # Skip first three days to give the network time to settle a proper initial state
        time_step = self._scenario_sim.epanet_api.get_hydraulic_time_step()
        n_steps_to_skip = int(to_seconds(days=3) / time_step)

        current_scada_data = None
        for _ in range(n_steps_to_skip):
            current_scada_data, _ = self._next_sim_itr()

        cur_time = int(current_scada_data.sensor_readings_time[0])
        hyd_scada = self._hydraulic_scada_data.extract_time_window(start_time=cur_time,
                                                                   end_time=cur_time)
        current_scada_data.join(hyd_scada)
        obs = self._get_observation(current_scada_data)

        return obs, {"scada_data": current_scada_data}

    def _next_sim_itr(self) -> Union[tuple[ScadaData, bool], ScadaData]:
        try:
            next(self._sim_generator)
            scada_data, terminated = self._sim_generator.send(False)

            if self.autoreset is True:
                return scada_data
            else:
                return scada_data, terminated
        except StopIteration:
            if self.autoreset is True:
                _, info = self.reset()
                return info["scada_data"]
            else:
                return None, True

    def get_hydraulic_scada_data(self) -> ScadaData:
        return self._hydraulic_scada_data

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, bool, dict]:
        # Apply actions
        for action_value, action in zip(action, self._action_space):
            action.apply(self, action_value)

        # Run one simulation step and observe the sensor readings (SCADA data)
        if self.autoreset is False:
            current_scada_data, terminated = self._next_sim_itr()
        else:
            terminated = False
            current_scada_data = self._next_sim_itr()

        if isinstance(current_scada_data, tuple):
            current_scada_data, _ = current_scada_data

        if current_scada_data is not None:
            cur_time = int(current_scada_data.sensor_readings_time[0])
            hyd_scada = self._hydraulic_scada_data.extract_time_window(start_time=cur_time,
                                                                       end_time=cur_time)
            current_scada_data.join(hyd_scada)
            obs = self._get_observation(current_scada_data)

            # Calculate reward
            current_reward = self._compute_reward_function(deepcopy(current_scada_data))
        else:
            obs = None
            current_reward = None

        # Return observation and reward
        return obs, current_reward, terminated, False, {"scada_data": current_scada_data}

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
