import jinja2
import os
from collections import defaultdict

PATH_TO_TEMPLATE = os.path.join(os.path.dirname(__file__), 'template.py')

def render_template(context, template_path=None):
    """
    Render a Jinja2 template.

    Parameters
    ----------
    template_path : str
        The path to the Jinja2 template.
    context : dict
        The context to render the template with.
    """
    template_path = template_path or PATH_TO_TEMPLATE
    with open(template_path, 'r') as f:
        template = jinja2.Template(f.read())
    return template.render(context)


def get_params_to_valid_domains(model):
    
    params_to_valid_domains = defaultdict(dict)

    for param, mech in model.params_to_mechs.items():
        for group_name, distribution in model.params[param].items():
            group = model.groups[group_name]
            valid_domains = [domain for domain in group.domains if mech == 'Independent' or mech in model.domains_to_mechs[domain]]
            params_to_valid_domains[param][group_name] = valid_domains

    return dict(params_to_valid_domains)