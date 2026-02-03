"""
This file contains code for creating new (random) contamination scenarios.
"""
import random
import math
import numpy as np
from epyt_flow.simulation import ScenarioSimulator, EpanetConstants


def create_random_contamination_event(time_window: tuple[int, int],
                                      duration_interval: tuple[int, int], n_time_steps: int):
    # Random point in time
    start_time = random.randint(time_window[0], time_window[1])

    # Random duration
    end_time = start_time + random.randint(duration_interval[0], duration_interval[1])

    # Random amount of contaminants
    EV_log_min = math.log10(1.39e6)
    EV_log_max = math.log10(2.08e7)
    EV_conc = 10 ** (EV_log_min + random.uniform(0, 1) * (EV_log_max - EV_log_min))
    TOC = 140 + random.uniform(0, 1) * (250 - 140)
    C_FRA_fraction = 0.4
    C_SRA_fraction = 0.6
    rate = 100

    injection_conc_P = EV_conc * rate
    injection_conc_C_FRA = C_FRA_fraction * TOC * rate
    injection_conc_C_SRA = C_SRA_fraction * TOC * rate

    profile_P = np.zeros(n_time_steps)
    profile_P[start_time:end_time] = injection_conc_P

    profile_C_FRA = np.zeros(n_time_steps)
    profile_C_FRA[start_time:end_time] = injection_conc_C_FRA

    profile_C_SRA = np.zeros(n_time_steps)
    profile_C_SRA[start_time:end_time] = injection_conc_C_SRA

    return ("P", profile_P), ("C_FRA", profile_C_FRA), ("C_SRA", profile_C_SRA)


if __name__ == "__main__":
    f_inp_in = "CY-DBP_competition_stream_competition_6days_0.inp"  # 6 days long scenario
    f_msx_in = "CY-DBP_competition_stream_competition_6days_0.msx"
    #f_inp_in = "CY-DBP_competition_stream_competition_365days.inp"   # 365 days long scenario
    #f_msx_in = "CY-DBP_competition_stream_competition_365days.msx"

    ########################################################################
    # Parameters of the contamination events
    duration_interval = (60, 480)    # 60 min - 480 min long contamination
    n_contamination_events = 2  # Two random contamination events
    time_window = (2, 5)        # Contamination event between the third and sixth day
    #n_contamination_events = 5  # Five random contamination events in the entire year
    #time_window = (5, 350)      # Contamination event between the sixth and 350th day
    ########################################################################

    # Create scenario
    with ScenarioSimulator(f_inp_in=f_inp_in, f_msx_in=f_msx_in) as scenario:
        # Setup time intervals
        hyd_time_step = scenario.get_hydraulic_time_step()  # Usually 5min time steps
        steps_per_day = (24 * 60 * 60) / hyd_time_step
        time_window = (time_window[0] * steps_per_day, time_window[1] * steps_per_day)
        duration_interval = ((duration_interval[0] * 60) / hyd_time_step,
                             (duration_interval[1] * 60) / hyd_time_step)
        n_time_steps = int(scenario.get_simulation_duration() / hyd_time_step)

        # Add random contamination events
        all_junctions = scenario.get_topology().get_all_junctions()
        contamination_patterns = []
        for _ in range(n_contamination_events):
            node_id = random.choice(all_junctions)

            contaminants_profiles = create_random_contamination_event(time_window, duration_interval,
                                                                      n_time_steps)
            for species_id, pattern in contaminants_profiles:
                contamination_patterns.append(pattern)
                scenario.add_species_injection_source(species_id, node_id, pattern,
                                                      EpanetConstants.EN_MASS)

        # Compute labels -- for each time step, 1 if a contamination present, 0 otherwise
        y = np.sum(contamination_patterns, axis=0) != 0
        #print(y.shape)  # TODO: Export labels

        # TEST: run simulation
        #scenario.place_bulk_species_node_sensors_everywhere(["P"])
        #scada_data = scenario.run_simulation(verbose=True)
        #scada_data.plot_bulk_species_node_concentration({"P": scenario.sensor_config.nodes})
