# Park et al. 2019

## Model description
Layer 2/3 pyramidal neuron from the mouse primary visual cortex (V1).

**Reference**: Park J., Papoutsi A., Ash R. T., Marin M. A., Poirazi P., Smirnakis S. M. (2019). Contribution of apical and basal dendrites to orientation encoding in mouse V1 L2/3 pyramidal neurons. Nature Communications 10:5372. https://doi.org/10.1038/s41467-019-13029-0

**Original source**: [ModelDB](https://modeldb.science/231185)

---

## Morphology

### `original.swc`
- **Description**: Original morphology
- **Base**: —
- **Modifications**: soma format

### `main.swc`
- **Description**: Main morphology used for simulations
- **Base**: `original.swc`
- **Modifications**: Node sorting, soma centering, apical alignment

### `main_reduced_apic.swc`
- **Description**: Apical tree reduced to a single section
- **Base**: `main.swc`
- **Modifications**: Morphology reduction, domain relabeling

### `main_block_na.swc`
- **Description**: A subtree of an apical branch marked as a custom domain for targeted manipulation of Na+ channels
- **Base**: `main.swc`
- **Modifications**: Domain relabeling

---

## Biophysics

### `main.json`
- **Description**: Main biophysical configuration with all mechanisms added
- **Base**: —
- **Compatible with**: `main.swc`

### `main_reduced_apic.json`
- **Description**: Biophysical configuration obtained during reduction
- **Base**: `main.json`
- **Compatible with**: `main_reduced_apic.swc`

### `main_block_na.json`
- **Description**: Biophysical configuration with all mechanisms added; Na+ channel conductance in the custom domain can be independently decreased
- **Base**: `main.json`
- **Compatible with**: `main_block_na.swc`

---

## Stimulation and recording protocols

### `current_soma_depol/`
- **Description**: Somatic injection of depolarizing current. Recording from the soma.
- **Compatible with**: All

### `current_soma_hyperpol/`
- **Description**: Somatic injection of hyperpolarizing current. Recording from the soma.
- **Compatible with**: All

### `syn_apic_50_ampa/`
- **Description**: 50 AMPA synapses distributed on the apical dendrite. Recording from the soma.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`

### `current_dend_hyperpol_attenuation/`
- **Description**: Dendritic injection of hyperpolarizing current. Recordings are placed along a path from a dendritic site to the soma to measure voltage attenuation.
- **Compatible with**:
    - Morphology: `main.swc`
    - Biophysics: `main.json`

### `current_soma_depol_block_na/`
- **Description**: Somatic injection of depolarizing current. Recordings are placed at the soma and two distant dendritic branches. This protocol can be used to assess how backpropagation of somatic action potentials depends on the presence of Na+ channels in the dendrites by selectively reducing Na+ conductance in one branch. For details see Figure 4 in Makarov et al. 2024.
- **Compatible with**:
    - Morphology: `main_block_na.swc`
    - Biophysics: `main_block_na.json`
