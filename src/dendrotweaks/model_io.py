import jinja2
import os
from collections import defaultdict

DOMAINS_TO_NEURON = {
    'soma': 'soma',
    'perisomatic': 'dend_11',
    'axon': 'axon',
    'apic': 'apic',
    'dend': 'dend',
    'basal': 'dend_31',
    'trunk': 'dend_41',
    'tuft': 'dend_42',
    'oblique': 'dend_43',
    'custom': 'dend_5',
    'reduced': 'dend_8',
    'undefined': 'dend_0',
}

def get_neuron_domain(domain_name):
    base_domain, _, idx = domain_name.partition('_')
    if base_domain in ['reduced', 'custom'] and idx.isdigit():
        return f'{DOMAINS_TO_NEURON[base_domain]}{idx}'
    return DOMAINS_TO_NEURON.get(base_domain, 'dend_0')

def render_template(path_to_template, context):
    """
    Render a Jinja2 template.

    Parameters
    ----------
    path_to_template : str
        The path to the Jinja2 template.
    context : dict
        The context to render the template with.
    """
    with open(path_to_template, 'r') as f:
        template = jinja2.Template(f.read())
    return template.render(context)


def get_params_to_valid_domains(model):
    
    params_to_valid_domains = defaultdict(dict)

    for param, mech in model.params_to_mechs.items():
        for group_name, distribution in model.params[param].items():
            group = model.groups[group_name]
            valid_domains = [get_neuron_domain(domain) for domain in group.domains if mech == 'Independent' or mech in model.domains_to_mechs[domain]]
            params_to_valid_domains[param][group_name] = valid_domains

    return dict(params_to_valid_domains)


def filter_params(model):
    """
    Filter out kinetic parameters from the model.

    Parameters
    ----------
    model : Model
        The model to filter.

    Returns
    -------
    Model
        The model with kinetic parameters filtered out.
    """
    filtered_params = {
        param: {
            group_name: distribution 
            for group_name, distribution in distributions.items() 
            if param in list(model.conductances.keys()) + ['cm', 'Ra', 'ena', 'ek', 'eca']} 
            for param, distributions in model.params.items()}
    return filtered_params