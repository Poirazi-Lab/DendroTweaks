# Hay et al. 2011

## Model description
Layer 5 pyramidal neuron from the rat somatosensory cortex.

**Reference**: Hay E., Hill S., Schürmann F., Markram H., Segev I. (2011). Models of Neocortical Layer 5b Pyramidal Cells Capturing a Wide Range of Dendritic and Perisomatic Active Properties. PLoS Computational Biology 7:e1002107. https://doi.org/10.1371/journal.pcbi.1002107

**Original source**: [ModelDB](https://modeldb.science/139653)

---

## Morphology

### `original.asc`
- **Description**: Original morphology in `.asc` format.
- **Base**: —
- **Modifications**: —

### `original.swc`
- **Description**: Original morphology in `.swc` format.
- **Base**: —
- **Modifications**: —

### `main.swc`
- **Description**: Main morphology used for simulations.
- **Base**: `original.swc`
- **Modifications**: Node sorting, soma centering, apical alignment.

### `main_fully_reduced.swc`
- **Description**: Each stem dendrite reduced to a single section.
- **Base**: `main.swc`
- **Modifications**: Morphology reduction, domain relabeling.

### `main_partially_reduced.swc`
- **Description**: Intermediate level of morphology reduction.
- **Base**: `main.swc`
- **Modifications**: Morphology reduction, domain relabeling.

---

## Biophysics

### `passive.json`
- **Description**: Biophysical configuration without active ion channels.
- **Base**: —
- **Compatible with**: `main.swc`

### `main.json`
- **Description**: Main biophysical configuration including all mechanisms.
- **Base**: —
- **Compatible with**: `main.swc`

### `main_fully_reduced.json`
- **Description**: Biophysical configuration obtained during reduction.
- **Base**: `main.json`
- **Compatible with**: `main_fully_reduced.swc`

### `main_partially_reduced.json`
- **Description**: Biophysical configuration obtained during reduction.
- **Base**: `main.json`
- **Compatible with**: `main_partially_reduced.swc`

---

## Stimulation and recording protocols

### `current_soma_depol/`
- **Description**: Somatic injection of depolarizing current; recordings at the soma.
- **Compatible with**: All

### `current_soma_hyperpol/`
- **Description**: Somatic injection of hyperpolarizing current; recordings at the soma.
- **Compatible with**: All

### `current_soma_hyperpol_attenuation/`
- **Description**: Somatic hyperpolarizing current injection with recordings placed along a path from a dendrite to the soma to measure voltage attenuation.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`

### `current_dend_hyperpol_attenuation/`
- **Description**: Dendritic hyperpolarizing current injection with recordings placed along a path from the dendrite to the soma to measure voltage attenuation.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`

### `syn_20_ampa_nmda_1_gabaa/`
- **Description**: 20 AMPA-NMDA synapses and 1 GABAa synapse placed within a single apical branch; recordings from the branch. See Figure 5 in Makarov et al. 2024 for details.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `passive.json`, `main.json`

### `current_syn_ca_spike/`
- **Description**: Somatic depolarizing current injection combined with an EPSP at the apical calcium "hot spot." Recordings are taken at the soma and at the "hot spot". This protocol can be used to observe generation of a dendritic Ca2+ plateau potential and the resulting somatic bursting. See Figure 4 in Makarov et al. 2024 for details.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`

### `syn_nonlinearity/`
- **Description**: Single AMPA-NMDA synapse placed on an apical dendritic branch. Dendritic nonlinearities are assessed by measuring dendritic voltage responses to increasing synaptic weights. See Figure 7 in Makarov et al. 2024 for details.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`
