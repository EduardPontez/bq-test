"""
    Script para tratar arquivos yaml
"""

import yaml

def custom_yaml_datetime(loader, node):
    """
        Está função evita que o PyYAML faça um parse de uma string para datetime.
    """
    try:
        return loader.construct_scalar(node)
    except ValueError:
        return None

yaml.add_constructor('tag:yaml.org,2002:timestamp', custom_yaml_datetime, Loader=yaml.SafeLoader)
