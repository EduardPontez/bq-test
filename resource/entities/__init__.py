"""
    Arquivo de inicialização de módulo para carregar todas as classes
    em tempo de execução dos componentes em tests.resource.entities
"""


import os, sys

path = os.path.dirname(os.path.abspath(__file__))

mockups = dict()

for py in [f[:-3] for f in os.listdir(path) if f.endswith('.py') and f != '__init__.py']:
    
    file = '.'.join(['tests.resource.entities', py])
    mod = __import__(file, fromlist=[py])

    classes = [getattr(mod, x) for x in dir(mod) if isinstance(getattr(mod, x), type) and x.upper() == 'MOCK']

    for cls in classes:
        setattr(sys.modules[__name__], cls.__name__, cls)
        mockups[py] = (cls)
