# Water Distribution Systems

> This section provides a brief overview of Water Distribution Systems, basic hydraulics and water quality principles. For a more thorough introduction, we recommend the [EPANET Documentation](https://epanet22.readthedocs.io/en/latest/index.html), especially sections [3. Network Model](https://epanet22.readthedocs.io/en/latest/3_network_model.html) and [12. Analysis Algorithms](https://epanet22.readthedocs.io/en/latest/12_analysis_algorithms.html).

A Water Distribution System (WDS) is a network of pipes that distributes drinking water from water sources and tanks to consumers. It is typically modeled as a graph $\mathcal{G} = (V, \mathcal{E})$ which consists of a set of nodes $V$ and a set of edges $(v, u) \in \mathcal{E}$.
The nodes correspond to either consumer nodes that may draw water out of the system, reservoirs that provide water, and tanks that can store and supply water. An edge connects two nodes $i$ and $j$ and corresponds to either a simple pipe, a pump or a valve.
Each node $v \in V$ is parameterized by an elevation $e_ v \in \mathbb{R}$ and a time series of demands $d_ v(t) \in \mathbb{R}_ {\geq 0}$. 
Each pipe $e \in E$ is parametrized by a length ${l}_ e \in \mathbb{R}_ {\geq 0}$, a diameter $\delta_ e \in \mathbb{R}_ {\geq 0}$ and a roughness coefficient ${C}_ e \in \mathbb{R}_{\geq 0}$.

![Example WDS Net1](/Figures/net1.png)
<small>Figure 1: An example WDS called *Net1*.</small>

### Hydraulics and Quality

There are two important dynamics in WDS, **hydraulics and quality**. 

The hydraulic state associates pressure heads to the nodes and flows to the pipes. Whenever two connected nodes have a different pressure head there is a flow from the node with the larger head to the node with the lower head. Usually the reservoir is considered a large enough water supply such that the pressure head is constant. For example, when water is drawn from a lake, the water level only drops marginally such that the pressure at a certain depth is constant over time.
The hydraulic state of the WDS changes when the demands at consumer nodes change, as the reservoir has to supply the corresponding amount and the flow conditions and thus the heads throughout the WDS have to adapt as well.

**Formally**, the hydraulic state is defined by pressure heads $\mathbf{h}(t) \in \mathbb{R}_{\geq 0}^{|V|}$ and flows $\mathbf{q}(t) \in \mathbb{R}^{|\mathcal{E}|}$. By convention, the flow at the edge $(v, u)$ is positive if water flows from node $v$ to node $u$ and negative otherwise.

There are three principles that govern the hydraulics:

1) Conservation of flows: The flow in a pipe from node $v$ to node $u$ is the negative of the flow of the pipe in opposite direction:

$$q_{vu}(t) = -q_{uv}(t).$$

2) Conservation of mass: The demand $d_u(t)$ at node $u$ at time $t$ has to be the same as the inflow minus the outflow of node $u$:

$$\sum_{v \in \mathcal{N}(u)} q_{vu}(t) = d_u(t).$$

3) Conservation of energy: The potential energy of pressure head converts to kinetic energy of flow. Importantly, the system looses energy due to friction which shows in the relationship between heads and flows. There are different mathematical models in the general form of $h_v - h_u = \Delta h_ {vu}(q_{vu})$.
An examle of such a model is the Hazen-Williams equation:

$$h_v(t) - h_u(t) = \Delta h_ {vu}(q_{vu}(t)) = \frac{4.727 ~ l_{vu}}{C_{vu}^{1.852} \delta_{vu}^{4.871}} ~ q_{vu}(t)^{1.852}.$$

The quality state tracks multiple chemicals or microorganisms of interest (also called *species*). Some typical examples of these species are fuoride, chorine, and a multitude of different bacteria. The quality state then corresponds to the concentrations of every specie of interest at every node.

**Formally**, the quality state is defined by concentrations $\mathbf{c}(t) \in \mathbb{R}_{\geq 0}^{|V| \times |S|}$, i.e. a feature vector for each node which specifies the concentration of species $s \in S$ at any time $t$.

The governing equations of the underlying dynamical system of water quality are the **advection-diffusion-reaction** equations, which are partial differential equations that describe the change of the concentrations over time:
 * Advection describes the transport of species through a liquid due to the flow of the liquid.
 * Diffusion is the spreading of species due to concentration gradients.
 * Reaction is the conversion of one or more species to (an-)other species. A reaction does not neccessarily involve multiple species, but includes degradation processes. The decay of chlorine, for example, can be modelled as a temporal degradation processes.

> Of the above equations, advection and reaction are typically dominating the dynamics. Diffusion is a comparably small effect.

![Advection PDE](/Figures/advection.png)
<small>Figure 2: A species distribution along space in a flow field undergoing advection plotted for 5 time steps.</small>

![Diffusion PDE](/Figures/dispersion_diffusion.png)
<small>Figure 3: A species distribution along space undergoing diffusion plotted for 10 time steps. Clearly regions of higher concentration distribute *mass* to regions of lower concentration.</small>

As a part of WDS management, operators have to frequently chlorinate the water to neutralize harmful contaminants. This is done at chlorine injection nodes. Below is an animation that shows spikes of chlorine injected at the reservoir node of the *Hanoi* WDS.
Note that we have added some nodes in between the original Hanoi nodes to better visualize how the chlorine propagates. The light blue area in the injection plot shows the total demand in the network at that time. As a consequence of the conservation of mass, this relates to the flow velocity and thus the velocity of the spikes traveling through the network.

<center>
    <video width="700" height="500" src="https://github.com/user-attachments/assets/a7317010-2c11-4daa-94df-bc3ffa813dc2" type="video/mp4" controls autoplay loop>
    </video>
</center>

