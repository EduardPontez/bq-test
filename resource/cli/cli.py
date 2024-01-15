"""
    Camada responsável pelo Commandline Interface da biblioteca.
"""

import pathlib
import argparse
from tests.resource.cli.arguments import arguments

class CLI:

    def __init__(self, cmd:str, filep:str):
        self.input = cmd
        self.parser = self._parser()
        self.args = self._args()
        self.suite = self._suite()
        self.testcase = self._testcase()
        self.persist_dataset = self._persist_dataset()
        self.home = self._home(filep)
        self.run = self._run()
        self.datasetid = self._datasetid()
        self.schema = self._schema()
        self.plt = False
        self.wlst = False
        self.dtq = False

    def _parser(self):
        """
            Retorna objeto para construção de argumentos.
        """
        return argparse.ArgumentParser(description='BQTest Library Automation')
    
    def _args(self):
        """
            Adiciona argumentos customizados para a library na leitura de suite e testcase.
        """        

        for arg in arguments:
            self.parser.add_argument(*arg["name"], **arg["kwargs"])

        return self.parser.parse_args()

    def _suite(self) -> list:
        """
            Obtém lista de suites informadas no CLI pela flag -s.
        """
        return self.args.suite

    def _testcase(self) -> list:
        """
            Obtém lista de testcases informados no CLI pela flag -t.
        """
        return self.args.testcase
    
    def _persist_dataset(self):
        """
            Obtém argumento para persistir o dataset informado no CLI pela flag -p.
        """
        return self.args.persist_dataset

    def _home(self, filep:str) -> str:
        """
            Obtém o diretório raiz em que se encontra a suite de testes.
            as_posix() converte para string objeto do tipo path.
        """
        target = pathlib.Path(filep).parents[0]

        return target.as_posix()
    
    def _run(self):
        """
            Indica se a execução da suite será efetuada(default) ou será feito em debbug para renderizar a query.
        """
        if str(self.args.run).lower() == 'false':
            return False 
        return self.args.run

    def _datasetid(self):
        """
            Parametro para indicar em qual dataset serão gravados os dados na execução da suite
        """

        return self.args.datasetid
    
    def _schema(self):
        """
            Indicar se o schema utilizado pela suite será atualizado 
        """

        return self.args.schema
