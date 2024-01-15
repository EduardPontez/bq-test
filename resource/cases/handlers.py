"""
    Script responsável por manter os métodos de SetUp e TearDown dos testes
    unitários e loader para a construção do testcases com controle de CLI.
"""

import unittest
import traceback
from functools import partial
from tests.resource.cli.cli import CLI
from tests.resource.utils import actions
from tests.resource.cases import asserts
from tests.resource.helpers import params
from tests.resource.api import logger as log
from tests.resource.utils.logger import logger
from tests.resource.utils import generator as gen
from tests.resource.utils import validator as val


class TestCase(unittest.TestCase):
    """
        Classe do Unittest onde as classes dos testes unitários
        herdarão os métodos de SetUp e TearDown.
    """

    failures = 0
    errors = False
    current = None
    start = None
    units = []

    @classmethod
    def setUpClass(cls):
        """
            SetUp do teste que inicia o contador, identifica qual teste
            unitário deve ser executado e aciona o Build para o Mocker.
        """

        try:
            # Inicia a contagem do teste
            cls.start = gen.datetime_from_current(string=False)
            cls.units.clear()

            # Aciona o Build do Mocker
            actions.setUpClass(path=str(cls.path), suite=cls.suite, testcase=cls.testcase)

        except Exception as e:
            tb = traceback.TracebackException.from_exception(e).__dict__
            error = log.LogError(trace=tb)
            log.send(error, target='log_error')
            raise e

    def setUp(self):
        """
            Para cada início de teste, verifica se em settings.py
            foi configurado para não executar a query do Motor de
            Regras. Neste caso, o status do teste será SKIP.
        """

        if not params.__HELPER__.run:
            self.skipTest('skipped')

    def tearDown(self):
        """
            Obtém o resultado do teste unitário executado
            e utiliza o logger para informar se passou ou falhou.
        """

        try:
            if self._outcome.errors[1][1] is not None and self._outcome.errors[1][1][0] != AssertionError:
                self.__class__.errors = True
                etype, value, tb = self._outcome.errors[1][1]
                trace = ''.join(traceback.format_exception(etype=etype, value=value, tb=tb, limit=-1))
                error = log.LogError(trace={'_str': value, 'stack': trace, 'exc_type': etype})
                log.send(error, target='log_error')
        except IndexError:
            pass    

        unitname = self._testMethodName
        
        unit = {
            'unitname': unitname,
            'expected': str(self.expected),
            'obtained': str(self.obtained)
        }

        self.__class__.units.append(unit)
        current = self.defaultTestResult()
        self.__class__.current = current
        
        self._feedErrorsToResult(current, self._outcome.errors)
        
        if len(self._outcome.skipped) == 1:
            logger.info(f'Skipped {unitname}')
        elif len(current.failures) == 0:
            logger.info(f'Passed {unitname}', extra={"color": "\033[32m"})
        else:
            logger.critical(f'Failed {unitname}')

        self.__class__.failures += len(current.failures)

    @classmethod
    def tearDownClass(cls):
        """
            Realiza o upload de resultados após todos os testes unitários
            presente na classe do Cenário finalizarem.
        """          

        elapsed = gen.datetime_from_current(string=False) - cls.start

        # Verifica se todos os testes unitários passaram
        if not cls.errors:
            if cls.current:
                if cls.failures == 0:
                    status = 'PASS'
                else:
                    status = 'FAIL'
            else:
                status = 'SKIP'

            actions.tearDownClass(status=status, duration=str(elapsed), units=cls.units)

class Loader:

    def __init__(self, cmd:str, filep:str):
        self.cli = self._cli(cmd=cmd, filep=filep)
        self.testcase = self._testcase()
        self.suite = self._suite()

    def _get_all_tests(self, suite:str) -> list:
        """
            Obtém o nome de todos os testcases IDs informados no arquivo yaml
        """
        filename = f'{self.cli.home}/suites/{suite}/test.yaml'
        return list(val.read_file(dir=filename).keys())
    
    def _cli(self, cmd:str, filep:str):
        """
            Instancia uma variável global que desce do params e retorna a própria instancia do CLI para o loader.
        """
        cli = CLI(cmd=cmd, filep=filep)
        params.__CLI__ = cli
        return cli

    def _testcase(self) -> list:
        """
            Propriedade responsável por montar uma lista de objetos unittest.TestCase com os
            métodos de asserções requeridos.

            # TODO: Complexidade Ciclomática nesta propriedade. Requer particionar melhor
            as divisões de montagem do testcase.
        """
        build_ups = list()

        # Inicia a montagem de acordo com a lista de suites informadas no CLI.
        if self.cli.suite is not None:
            
            for suite in self.cli.suite:
                
                # Obtém a lista de testcases informadas pelo CLI. Caso nenhum for informado, todos são considerados.
                list_cases = self.cli.testcase if self.cli.testcase is not None else self._get_all_tests(suite)
                
                for testcase in list_cases:
                    
                    path = f'{self.cli.home}/suites/{suite}/test.yaml'

                    # Cria uma nova classe abstrata de TestCase conforme o nome do testcase ID.
                    tc = type(testcase, (TestCase,), {})

                    # Informa ao TestCase o caminho, a suite e o testcase a serem usados pelo SetupClass
                    setattr(tc, 'path', path)
                    setattr(tc, 'suite', suite)
                    setattr(tc, 'testcase', testcase)

                    # Obtém o nome dos métodos para testes unitários.
                    tests_to_apply = self._required(testcase, suite)

                    for value, expected in tests_to_apply.items():

                        broken_target = value.split('should')
                        field = broken_target[0][:-1]
                        name_target = broken_target[-1]
                        name_target = ''.join(name_target)
                        name_target = f'should{name_target}'
                        
                        # Atualiza a instância do objeto de Testcase para agregar os métodos.
                        fun = getattr(asserts, name_target)
                        unit_append = partial(fun, tc, value=expected, expected=value, field=field)
                        unit_append.__doc__ = ''
                        setattr(tc, f'test_{value}', unit_append)         

                    build_up = unittest.TestLoader().loadTestsFromTestCase(tc)
                    build_ups.append(build_up)
                
        return build_ups

    def _suite(self):
        """
            Cria objeto de Suite de teste do unittest com a lista de testcases montados.
        """
        return unittest.TestSuite(self.testcase)

    def _required(self, testcase:str, suite:str) -> dict:
        
        filename = f'{self.cli.home}/suites/{suite}/test.yaml'
        target = val.read_file(dir=filename)

        if 'unittests' not in target[testcase].keys():
            raise Exception('Testcase does not unittests settings.')
        return target[testcase]['unittests']
