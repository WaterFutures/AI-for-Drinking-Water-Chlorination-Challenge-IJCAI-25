# 1st AI for Drinking Water Chlorination Challenge @ IJCAI-2025

This challenge is about controlling the chlorination for mitigating and reacting to wastewater contamination events and other time-varying dynamics in a water distribution system simulation. Note that Chlorine is added to water distribution systems primarily as a disinfectant to kill harmful bacteria, viruses, and other pathogens, ensuring safe drinking water.

*The task is to control the injection of chlorine (Cl) at 5 locations, based on the readings of a few strategically placed hydraulic and chlorine sensors only.*

Background information about the task and the scenario is provided [here](scenario_desc.md), while general information on water distribution systems and their dynamics can be found [here](<Introduction WDNs, Hydraulics and Quality.md>).

You can find a set of frequently asked questions [here](faq.md).

## Results

Evaluations are running -- the results will be published as soon as possible.

## Update 30th July

- Specify time zone on deadline (it is AoE)
- Downgrade a dependency which seems to cause problems on Windows -- please use epyt==1.2.2 if you are working on Windows.

## Update 19th July

- Deadline extended to **4th August**

- `load_scenario()` uses pre-computed hydraulic dynamics to speed up the entire simulation

## Update 5th June

- Release of a $365$-day long scenario.

> **_NOTE:_** The $365$-day long scenario is quite large and is therefore handled by [Git LFS](https://git-lfs.com/). Alternatively, if you do not want to install [Git LFS](https://git-lfs.com/), you can download the release of this repository, which contains all files (incl. the large ones).

## Update 2nd June

- Release of five additional $6$-day long scenarios.
- Implementation of the infection risk metric (see [evaluation.py](evaluation.py))

## Timeline

All deadlines are AoE.

**Competition meta data release:** 6th May, 2025 &#10004;

**Release of first scenarios:** 12th May, 2025 &#10004;

**Release of additional scenarios:** 2nd June, 2025 &#10004;

**Submission deadline:** 4th August, 2025 &#10004;

**Notification of results and publication of test set:** 11th August, 2025

**Presentation of results at IJCAI 2025:** Montreal, 16th -- 22nd August, 2025


## Evaluation

The evaluation will be done on a secrete $365$ days long scenario, similar to the one already provided. You can assume that the secret test scenario will be of the same form -- i.e., $365$ days long, same network, and same sensors and chlorine injection pumps. However, there will be slightly different water demands, slight changes in the TOC concentrations, and random contamination events.

Submissions will be evaluated on the following metrics (all to be minimized):
- Total amount of injected chlorine -- i.e., control cost.
- Satisfaction of chlorine injection pump operation constraints, such as maximum injection and injection rate of change.
- Local satisfaction of pre-defined chlorine concentration bounds.
- Infection risk.
- Spatial variations of the two aforementioned metrics, evaluating a particular notion of fairness.

Submissions will be ranked according to their performance on those individual aspects for each test scenario, as well as a global ranking where all aspects and criteria are considered.
The top-performing teams will receive a certificate.

More details about the evaluation metrics can be found [here](evaluation.md).

## Starter code

Participants are provided with a set of scenario configurations/environments, constituting the same water distribution network but with varying contamination events and uncertainties. A Python interface, which abstracts away from all water distribution system details, is provided for a step-by-step simulation of these scenario configurations. This Python interface is implemented utilizing the [EPyT-Control package](https://github.com/WaterFutures/EPyT-Control), which is fully compatible with the [Gymnasium interface](https://gymnasium.farama.org/) and integrates the popular [Stable-Baselines3 package](https://stable-baselines3.readthedocs.io/en/master/). 

### Requirements

All requirements are listed in [REQUIREMENTS.txt](REQUIREMENTS.txt).
Please note that EPyT-Control builds on top of [EPyT-Flow](https://github.com/WaterFutures/EPyT-Flow) which comes with pre-compiled shared libraries for running the hydraulic and water quality simulations. In rare cases those might cause compatibility issues -- in those cases, as well as in order to fully make use of your local CPU, you may want to re-compile those libraries as described in the [documentation](hhttps://epyt-flow.readthedocs.io/en/stable/installation.html).

### The environment

The provided environments are derived from the [WaterChlorinationEnv](env.py) class, which mimics the [Gymnasium Environment](https://gymnasium.farama.org/api/env/) interface. Note that the `WaterChlorinationEnv` class is an instantiation of [EpanetMsxControlEnv](https://epyt-control.readthedocs.io/en/stable/epyt_control.envs.html#epyt_control.envs.advanced_quality_control_env.EpanetMsxControlEnv) from the [EPyT-Control package](https://github.com/WaterFutures/EPyT-Control).

The environment has to be initialized with a scenario configuration, which can be loaded using the `load_scenario()` function from the [scenarios.py](scenarios.py) file -- note that you have to specify the ID of the scenario. We provide a total of **ten** $6$-day long scenarios for facilitating the training of ML-based methods -- note that all scenarios are for the same water network (same sensors and chlorine injection pumps) but with different (randomized) contamination events.
Furthermore, there is also an $11th$ scenario available, which is $365$ days long. You can assume that the secret test scenario will be of the same form -- i.e., $365$ days long, same network, and same sensors and chlorine injection pumps.
Note that the simulation of the $365$-day long scenario takes a considerable amount of time. We recommend to start with the $6$-day long scenarios.

In order to speed up things, `load_scenario()` uses on pre-computed hydraulic dynamics that are first downloaded if not already present in this folder. Users can decide not to use those by setting the parameter `use_precomputed_hydraulics=True` in the `load_scenario()` function -- in this case, the hydraulics are computed first before the user can start interacting with the environment.

Usage:

```python
# Load the first environment (i.e., scenario 0)
with WaterChlorinationEnv(**load_scenario(scenario_id=0)) as env:
    # Reset environment and observe initial sensor readings
    # obs: 19 dimensional array (one dimension per sensor) --
    # first 2 dimensions contain the flow sensors, and the remaining 17 dimensions the chlorine concentration sensors
    obs, info = env.reset()

    for _ in range(20): # Run environment for up to 20 time steps
        # TODO: Your control logic goes here
        act = env.action_space.sample() # Sample random action

        # Apply action, observe new sensor readings and receive reward
        obs, reward, terminated, _, _ = env.step(act)

        if terminated is True:
            break
``` 

### Custom reward function

The provided `WaterChlorinationEnv` class comes with a simple reward function implemented in `_compute_reward_function()`. Participants are encouraged to override this function and implement their own reward function. Here, simulated system states, given as a [ScadaData](https://epyt-flow.readthedocs.io/en/stable/epyt_flow.simulation.scada.html#epyt_flow.simulation.scada.scada_data.ScadaData) instance, are mapped to a reward.

### Interface for policies/controllers

For the final submission, but also in order to be able to run the implemented evaluation metrics, all policies/controllers must be instances of [ChlorinationControlPolicy](control_policy.py). Here, the abstract method `compute_action()` must be overridden. This method maps the sensor readings ($19$ dimensional NumPy array) to actions ($5$ dimensional NumPy array), i.e., injection rate of Chlorine for each of the three injection pumps.

Example of a random policy:
```python
class ChlorinationControlPolicyRandom(ChlorinationControlPolicy):
    """
    Random control policy -- picks random control actions.
    """
    def compute_action(self, observations: numpy.ndarray) -> numpy.ndarray:
        return self._gym_action_space.sample()


# Apply to the environment of scenario 0
with WaterChlorinationEnv(**load_scenario(scenario_id=0)) as env:
    # Create new random policy
    my_policy = ChlorinationControlPolicyRandom(env)

    # Reset environment
    obs, info = env.reset()

    for _ in range(20):
        # Apply policy
        act = my_policy.compute_action(obs)
        obs, reward, terminated, _, _ = env.step(act)

        if terminated is True:
            break
``` 

All evaluation metrics are already implemented in the function `evaluate()` in the file [evaluation.py](evaluation.py):
```python
# Create and fit policy
my_policy = ...

# Load load one environment for evaluation
env = ....

# Evaluate policy
print(evaluate(my_policy, env))
``` 

Note that this is exactly how the submissions will be evaluated. Therefore, participants must implement their method as an instance of the `ChlorinationControlPolicy` class.
Please see [example.py](example.py) for a complete but minimalistic example of how to correctly use the provided evaluation code.

## Submissions

Participants have to submit the source code, the trained model (`ChlorinationControlPolicy` instance), and a short written report.
The written report has to be submitted via the [EasyChair platform](https://easychair.org/conferences?conf=ai4dwc25), and everything else (i.e., source code and the trained model) via the following link as a single .zip file: [Upload-Link](https://u.pcloud.com/#page=puplink&code=sX4XZms5B1cm4FQbpuVCmG9BOy8K0WvR7).
For the written report, please use the [IJCAI LaTeX template](https://www.ijcai.org/authors_kit) -- note that there is no page limit for the written report.

The submitted Python code must contain a **REQUIREMENTS.txt** file and contain a file **load_my_policy.py**, which contains a method
`load_policy(env: WaterChlorinationEnv) -> ChlorinationControlPolicy`
that returns the final controller/policy (i.e., `ChlorinationControlPolicy` instance) .
Please see [example-submission](example-submission) folder for an example of how to structure and organize a submission.

The evaluation will be done by the organizing commitee on a secret set of test scenarios where the uncertain parameters will vary within predetermined bounds, to evaluate the generalization -- i.e., a proxy for evaluating the sim-to-real gap. The test scenarios will be made public after the submission deadline.

All submissions, including reports, source code, and final results, will be published on this webpage.
Participants are invited to present their results in the on-site session at IJCAI-2025. Please indicate in your submission whether you plan to attend and present at the on-site session.

## Contact

André Artelt -- aartelt@techfak.uni-bielefeld.de

### Organizing Committee
- André Artelt *-- Bielefeld University, Germany*
- Luca Hermes *-- Bielefeld University, Germany*
- Janine Strotherm *-- Bielefeld University, Germany*
- Barbara Hammer *-- Bielefeld University, Germany*
- Stelios G. Vrachimis *-- University of Cyprus, Cyprus*
- Marios S. Kyriakou *-- University of Cyprus, Cyprus*
- Demetrios G. Eliades *-- University of Cyprus, Cyprus*
- Marios M. Polycarpou *-- University of Cyprus, Cyprus*
- Sotirios Paraskevopoulos *-- Center for Research and Technology Hellas, Greece*
- Stefanos Vrochidis *-- Center for Research and Technology Hellas, Greece*
- Riccardo Taormina *-- TU Delft, Netherlands*
- Dragan Savic *-- KWR, Netherlands*
- Phoebe Koundouri *-- Athens University of Economics and Business, Greece*


## License

MIT license -- see [LICENSE](LICENSE)

## How to Cite?

If you use material from this competition, please cite it as follows:

Artelt, A., Hermes, L., Strotherm, J., Hammer, B., Vrachimis, S. G., Kyriakou, M. S., Eliades, D. G., Polycarpou, M. M., Paraskevopoulos, S., Vrochidis, S., Taormina, R., Savic, D., & Koundouri, P. (2025). *1st AI for Drinking Water Chlorination Challenge* (Competition/Challenge). 34th International Joint Conference on Artificial Intelligence (IJCAI), Montreal, Canada.

Alternatively, you may use the following BibTex entry:
```
@misc{github:ai4drinkwaterchlorinationchallenge25,
        author = {André Artelt and Luca Hermes, Janine Strotherm and Barbara Hammer and Stelios G. Vrachimis and Marios S. Kyriakou, Demetrios G. Eliades and Marios M. Polycarpou and Sotirios Paraskevopoulos and Stefanos Vrochidis and Riccardo Taormina and Dragan Savic and Phoebe Koundouri},
        title = {{1st AI for Drinking Water Chlorination Challenge}},
        year = {2025},
        publisher = {34th International Joint Conference on Artificial Intelligence (IJCAI)}
        howpublished = {\url{https://github.com/WaterFutures/AI-for-Drinking-Water-Chlorination-Challenge-IJCAI-25}}
    }
```
