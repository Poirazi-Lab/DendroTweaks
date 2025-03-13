import jinja2
import os
import shutil


def render_template(template_path, context):
    """
    Render a Jinja2 template.

    Parameters
    ----------
    template_path : str
        The path to the Jinja2 template.
    context : dict
        The context to render the template with.
    """
    with open(template_path, 'r') as f:
        template = jinja2.Template(f.read())
    return template.render(context)