"""
    Script responsável por iniciar a rotina de
    execução dos testes.
"""

import sys
import unittest

sys.path.append('.')
from tests.resource.cases.handlers import Loader  

l = Loader(cmd=sys.argv, filep=__file__)
unittest.TextTestRunner(descriptions=0, verbosity=0).run(l.suite)
