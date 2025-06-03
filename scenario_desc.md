# Scenario Description

This challenge reflects real-world complexity:

- Water demands change constantly
- Source water quality varies
- Sensor data is limited
- Contamination can happen unexpectedly

## The Water Distribution Network

The water distribution network (WDN) supplies drinking water from a treatment plant and includes both treated and desalinated sources.
It consists of:

- 256 demand nodes (where people consume water),
- 335 pipes connecting everything,
- 1 reservoir (`WTP`, the main water source), and
- 1 elevated tank (`T_Zone`) that helps regulate pressure.

Water flows from the reservoir into the network, through the pipes, and eventually reaches homes, businesses, and other consumers.

![The Water Distribution Network](Figures/cydbp.png)

## Your Control Levers: Booster Stations
You can control five chlorine injection pumps, located at:

- `dist423`
- `dist225`
- `dist989`
- `dist1283`
- `dist1931`

Each booster can inject from 0 up to $10000$ mg/L of chlorine.
Your control policy decides the injection amount every 5 minutes.

![Chlorine booster stations](Figures/booster_stations.png)


## Sensor Data
To make decisions, your control policy receives the following inputs:

- Chlorine levels at a limited number of monitoring nodes:
    - `dist423`
    - `dist225`
    - `dist989`
    - `dist1283`
    - `dist1931`
    - `dist342`
    - `dist275`
    - `dist354`
    - `dist885`
    - `dist485`
    - `dist631`
    - `dist1332`
    - `dist1607`
    - `dist1459`
    - `dist1702`
    - `dist1975`
    - `dist1903`
- Flow measurements at a few selected pipes:
    - `5`
    - `p-1144`

This setup mimics real-life conditions, where sensors are only available at selected locations.

![Chlorine sensor nodes](Figures/sensor_nodes.png)


## Simulation Details
The simulation covers, depending on the sceanrio, either six days or one full year, at a resolution of 5 minutes per step.
At each step:

- Demands vary across the network,
- Water flows are recalculated,
- Chlorine reacts with organic matter and decays,
- Your controller can take action at the booster stations.

Note that the first 3 days of the scenario simulation are hidden from the user, who starts interacting with the network (i.e., controlling the chlorine injection) at day 4. This is to make sure that the network is in a realistic starting state, when it comes to chlorine residuals at all nodes.

## Variable Water Demands

Water use changes throughout the day (typically higher in mornings and evenings).
It also changes seasonally, higher in summer and lower in winter.
Each node has a unique demand profile generated using detailed simulations of daily household water use.
Monthly seasonality is added using predefined multipliers.

## Variable Water Quality
Water enters the network with:

- A random chlorine concentration (between 0.4–0.6 mg/L),
- A variable level of organic matter, which reacts with and reduces chlorine.
- Organic matter levels change month by month, based on seasonal patterns.

This makes chlorine decay behavior unpredictable and adds uncertainty to the disinfection process.

## Contamination Events (Hidden Challenges)
There are 15 (or 1 in the case of a six day scenario) contamination events introduced at random times during the simualtion period.
Each event:

- Happens at a random node (not known in advance),
- Lasts between 1 to 8 hours,
- Injects pathogens and extra organic matter into the system.

Your control policy won’t know when or where these happen.

Your goal is to maintain chlorine concentration  ≥ 0.2 mg/L but <= 0.4 mg/L throughout the network. 

This concentration is critical to effectively neutralize pathogens, ensuring that water remains microbiologically safe for consumers. At the same time, maintaining chlorine levels below 0.4 mg/L minimizes the risk of adverse effects, such as unpleasant taste and odor, while also reducing the formation of potentially harmful chlorine by-products, such as trihalomethanes (THMs) and haloacetic acids (HAAs).
