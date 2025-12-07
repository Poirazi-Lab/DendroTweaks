# Poirazi et al. 2003

## Model description
CA1 pyramidal neuron model.

**Reference**: Poirazi P., Brannon T., Mel B. W. (2003). Pyramidal neuron as a two-layer neural network. Neuron 37: 989–999. https://doi.org/10.1016/S0896-6273(03)00149-1

**Original source**: [ModelDB](https://modeldb.science/20212)

---

## Morphology

### `original.swc`
- **Description**: Original morphology.
- **Base**: —
- **Modifications**: —

### `main.swc`
- **Description**: Main morphology used for simulations.
- **Base**: `original.swc`
- **Modifications**: Node sorting, soma format, soma centering, apical alignment.

---

## Biophysics

### `main.json`
- **Description**: Main biophysical configuration with all mechanisms included.
- **Base**:
- **Compatible with**: `main.swc`

### `main_blocked_ih.json`
- **Description**: Biophysical configuration with all mechanisms; HCN (Ih) channel conductance reduced by 80% throughout the cell.
- **Base**: `main.json`
- **Compatible with**: `main.swc`

---

## Stimulation and recording protocols

### `current_soma_depol/`
- **Description**: Somatic injection of depolarizing current; recordings from the soma.
- **Compatible with**: All

### `current_soma_dend_hyperpol_blocked_ih/`
- **Description**: Proximal current step injected followed, after 300 ms, by a distal step in the apical trunk. Recordings are taken from the same positions. For more details, see Figure 4 in Makarov et al. (2024).
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main_blocked_ih.json`

### `syn_40_ampa_nmda_clustered/`
- **Description**: 40 AMPA–NMDA synapses clustered within five randomly selected branches of the apical dendrite. Recordings from soma and dendrites. For more details, see Figure 5 in Makarov et al. (2024).
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`

### `syn_40_ampa_nmda_distributed/`
- **Description**: 40 AMPA–NMDA synapses distributed across the apical dendrite. Recordings from soma and dendrites. For more details, see Figure 5 in Makarov et al. (2024).
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`
