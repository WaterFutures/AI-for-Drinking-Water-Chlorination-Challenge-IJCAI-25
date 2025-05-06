# 1st AI for Drinking Water Chlorination Challenge @ IJCAI-2025

This challenge is about controlling the chlorination for mitigating and reacting to wastewater contamination events and other time-varying dynamics in a water distribution system simulation.

*The task is to control the injection of chlorine (Cl) at 5 locations, based on the readings of a few strategically placed sensors only.*

Background information about the task and the scenario will be provided, and general information on water distribution systems and their dynamics can be found [here](<Introduction WDNs, Hydraulics and Quality.md>).

## Timeline

**Competition meta data release:** 6th May, 2025

**Release of first scenarios:** 12th May, 2025

**Release of additional scenarios:** 2nd June, 2025

**Submission deadline:** 1st August, 2025

**Notification of results and publication of test set:** 8th August, 2025

**Presentation of results at IJCAI 2025:** Montreal, 16th -- 22nd August, 2025

## Evaluation

Submissions will be evaluated on the following metrics:
- Total amount of injected chlorine -- i.e., control cost.
- Satisfaction of chlorine injection pump operation constraints, such as maximum injection and injection rate of change.
- Local satisfaction of pre-defined chlorine concentration bounds.
- Infection risk.
- Spatial variations of the two aforementioned metrics, evaluating a particular notion of fairness.

Submissions will be ranked according to their performance on those individual aspects for each test scenario, as well as a global ranking where all aspects and criteria are considered.

More details about the evaluation metrics can be found [here](evaluation.md).

## Starter code

Participants will be provided with a set of scenario configurations/environments, constituting the same water distribution network but with varying contamination events and uncertainties. A Python interface, which abstracts away from all water distribution system details, is provided for a step-by-step simulation of these scenario configurations. This Python interface is implemented utilizing the [EPyT-Control package](https://github.com/WaterFutures/EPyT-Control), which is fully compatible with the [Gymnasium interface](https://gymnasium.farama.org/) and integrates the popular [Stable-Baselines3 package](https://stable-baselines3.readthedocs.io/en/master/). 

### Requirements

All requirements are listed in [REQUIREMENTS.txt](REQUIREMENTS.txt).
Please note that EPyT-Control builds on top of [EPyT-Flow](https://github.com/WaterFutures/EPyT-Flow), which comes with pre-compiled shared libraries for running the hydraulic and water quality simulations. In rare cases those might cause compatibility issues -- in those cases, as well as in order to fully make use of your local CPU, you may want to re-compile those libraries as described in the [documentation](hhttps://epyt-flow.readthedocs.io/en/stable/installation.html).



## Submissions

Participants have to submit the source code, the trained model, and a short written report.
The written report has to be submitted via the [EasyChair platform](https://easychair.org/conferences?conf=ai4dwc25), and everything else (i.e., source code and the trained model) via the following link as a single .zip file: [Upload-Link](https://u.pcloud.com/#page=puplink&code=sX4XZms5B1cm4FQbpuVCmG9BOy8K0WvR7).
For the written report, please use the [IJCAI LaTeX template](https://www.ijcai.org/authors_kit) -- note that there is no page limit for the written report.

The submitted Python code must contain a **REQUIREMENTS.txt** file and contain a file **load_my_policy.py**, which contains a method
`load_policy(env: WaterChlorinationEnv) -> ChlorinationControlPolicy`
that returns the final controller/policy (i.e., `ChlorinationControlPolicy` instance).
Please see [example-submission](example-submission) folder for an example of how to structure and organize a submission.

The evaluation will be done by the organizing commitee on a secret set of test scenarios where the uncertain parameters will vary within predetermined bounds, to evaluate the generalization -- i.e., a proxy for evaluating the sim-to-real gap. The test scenarios will be made public after the submission deadline.

All submissions, including reports, source code, and final results, will be published on this webpage.
Participants are invited to present their results in the on-site session at IJCAI-2025. Please indicate in your submission whether you plan to attend and present at the on-site session.

## Contact

André Artelt -- aartelt@techfak.uni-bielefeld.de

### Organizing Committee
- André Artelt *-- Bieleld University, Germany*
- Luca Hermes *-- Bieleld University, Germany*
- Janine Strotherm *-- Bieleld University, Germany*
- Barbara Hammer *-- Bieleld University, Germany*
- Stelios G. Vrachimis *-- University of Cyprus, Cyprus*
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

Artelt, A., Hermes, L., Strotherm, J., Hammer, B., Vrachimis, S. G., Eliades, D. G., Polycarpou, M. M., Paraskevopoulos, S., Vrochidis, S., Taormina, R., Savic, D., & Koundouri, P. (2025). *1st AI for Drinking Water Chlorination Challenge* (Competition/Challenge). 34th International Joint Conference on Artificial Intelligence (IJCAI), Montreal, Canada.
