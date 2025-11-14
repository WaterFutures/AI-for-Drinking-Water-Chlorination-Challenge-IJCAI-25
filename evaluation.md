# Evaluation Procedure

Water chlorination control constitutes a complex multi-objective optimization problem.
Consequently, submitted control strategies/policies are evaluated with respect to different criteria (all to be minimized).
Submissions will be ranked according to their performance on those individual aspects for
each test scenario, as well as a global ranking where all aspects and criteria are considered (uniform weighting).

In order to assess how well the submitted methods generalize (i.e., evaluate the sim-to-real gap),
the evaluation is done on a secret set of test scenarios, where some of those test scenarios feature
slightly different dynamics in order to evaluate the generalization.

## Violations of Chlorine Concentration Bounds

In order to ensure safe drinking water at all times, the chlorine concentration at junctions must be within a given bound -- i.e., to low chlorine concentrations can not ensure safe drinking water, whereas too high chlorine concentrations are known to be unhealthy for the human body. Usually, those bounds are specified in legal regulations.

For each junction $v$, the chlorine concentration $c_v$ must be within a given interval $[a,b]$ at all times:

$$
\frac{1}{T} \sum_{t=1}^T \mathbf{1}_{[a,b]}(c_v(t))
$$

where $\mathbf{1}_{[a,b]}(c_v(t))=1$ iff $c_v(t)\in[a,b]$.

We aggregate over all junctions $V$ by taking the average:

$$
\frac{1}{T|V|}\sum_{v\in V} \sum_{t=1}^T \mathbf{1}_{[a,b]}(c_v(t))
$$

In this challenge, we use $[0.2, 0.4]\text{mg/l}$ as desired chlorine concentration bounds.


## Fairness

While the aforementioned metrics evaluate some quantity of interest at a particular junction, we also evaluate their spatial variations:

$$
\underset{v1, v2 \in V}{\max} \, |s_{v1} - s_{v2}|
$$

where $s_i$ refers to the quantity of interest at junction $i$ -- i.e., either the violations of chlorine concentration bounds or the infection risk.

By this, we evaluate some form of fairness where we evaluate the worst-case of how different all junctions (i.e., consumers) or contamination event locations are treated.


## Infection Risk

The infection risk is an evaluation metric that quantifies the public health impact by estimating the probability of an individual getting ill after exposure to pathogens during a contamination event. Following the Quantitative Microbial Risk Assessment (QMRA) framework, it combines the pathogen concentration, the water consumption behavior, and finally dose-response modeling. The dose for each individual is calculated by multiplying the pathogen concentration in drinking water by the ingested volume across multiple daily consumption events, totaling up to 1 liter per person per day. For enterovirus, the infection probability is derived using an exponential dose-response model: 

$$
Risk = 1 - \exp(-r * Dose)
$$

with $r = 0.014472$ representing the pathogen-specific infectivity. The infection risk is then defined as the ratio of expected infections to the total population. This metric evaluates how well the controller prevents (or minimizes) health risks during an (undetected) contamination event.

Note that in contrast to the other evaluation metrics, the infection risk is computed for each contamination event only.


## Smoothness of Chlorine Injection

From an operational point of view, it is unhealthy or even unrealistic for chlorine injection pumps to have large changes/jumps in the injection rate. We therefore evaluate the *smoothness* of the chlorine injection over time.

The average rate of change w.r.t. the chlorine injection $u_v$ at junction $v$ is evaluated as:

$$
\frac{1}{T-1}\sum_{t=1}^{T-1} |u_v(t) - u_v(t+1)|
$$

In this challenge, we have five chlorine injection pumps, $v_1$ to $v_5$. Consequently, we take the maximum over their average rate of change as the final evaluation, which is to be minimized:

$$
\underset{v \in \{v_1, .., v_5\}}{\max}\, \frac{1}{T-1}\sum_{t=1}^{T-1} |u_v(t) - u_v(t+1)|
$$


## Cost of Control

In this challenge, we model the cost of control, which is to be minimized, as the amount of injected chlorine at the five chlorine injection pumps $v_1$ to $v_5$:

$$
\sum_{t=1}^{T} \sum_{j=1}^5 u_{v_j}(t)
$$
