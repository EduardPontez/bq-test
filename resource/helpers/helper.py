"""
    1º script a ser iniciado para execução de rotina no Data Mock para o setUp
    dos testes. Responsável por determinar as configurações iniciais do ambiente.
"""

import os
from pathlib import PurePath
from socket import gethostname
from tests.resource.helpers import params
from tests.resource.api.client import Client
from tests.resource.utils import validator as val
from tests.resource.helpers.config import SuiteConfig
from tests.resource.utils.governance import Governance


class Helper:

    """
        Classe responsável por iniciar e determinar as configurações do ambiente
        para a execução do Data Mock.
    """

    def __init__(self, path: str = None, suite: str = None, testcase: str = None):
        self.suite = suite
        self.testcase = testcase
        self.config = self._config(path)
        self.hostname = self._hostname()
        self.environment = self._enviroment()
        self.local = self._local()
        self.project_id = params.__PROJECT_ID__
        self.project_id_mtd = self._project_id_mtd()
        self.dataset_id = self._dataset_id()
        self.dataset_utils = params.__DATASET_UTILS__
        self.dataset_logs = params.__DATASET_LOGS__
        self.dataset_mtd = params.__DATASET_MTD__
        self.references = params.__REFERENCES__
        self.run = self._run()
        self.sch = self._sch()
        self.wlst = self._wlst()
        self.default = self._default()
        self.plt = self._plt()
        self.dtq = self._dtq()
    
    def _config(self, path):

        """
            Cria instância de configuração da suite para disponibilidade de 
            decisão do Helper.
        """
        return SuiteConfig(path=path)

    def _hostname(self) -> str:
        """
            Retorna o hostname do ambiente que executa a rotina de Data Mock.
        """
        return gethostname().upper()

    def _enviroment(self) -> str:

        """
            Função que determina se o ambiente que executa a rotina
            é local ou do Airflow.

            Se o ambiente tiver variável de ambiente AIRFLOW_HOME e o nome
            hostname conter airflow-worker, será considerado Cloud.
        """
        
        if 'AIRFLOW_HOME' in os.environ and 'AIRFLOW-WORKER' in self.hostname.upper():
            try:
                from airflow.models import Variable
                return Variable.get('environment').upper()
            except ImportError:
                raise Exception('Airflow does not have environment variable.')
        return 'LOC'

    def _local(self) -> bool:
        """
            Retorna True se o environment for LOC.
            Retorna False para qualquer outro valor diferente.
        """

        return True if self.environment == 'LOC' else False

    def _dataset_id(self) -> str:
        """
            Obtém o dataset_id de acordo com o ambiente que
            executa a rotina.
        """

        if not self.local:
            return self.config.default_dataset_test

        else:
            dataset_from_settings = params.__CLI__.datasetid

            # Se o ambiente for cloud ou não for informado dataset_id em ambiente local,
            # então o default será dataset que nunca é recriado.

            if dataset_from_settings == '':
                return self.config.default_dataset_test

            # Verifica se o nome informado foi digitado com prefixo mock_
            elif dataset_from_settings == self.config.default_dataset_test \
                or dataset_from_settings == params.__DATASET_LOGS__ \
                or dataset_from_settings == params.__DATASET_UTILS__:
                raise Exception('You cannot use a reserved dataset_id')

            else:
                # Valida se o nome informado inicia com prefixo
                Governance().check_dataset_name(dataset_from_settings)

            return dataset_from_settings
        

    def _project_id_mtd(self):
        """
            Função que determina qual PROJECT_ID (hml ou prd) utilizado para
            consulta na tabela de metadata.
        """

        return params.__PROJECT_ID_MTD_HML__ if self.environment == 'HML' else params.__PROJECT_ID_MTD_PRD__

    def _default(self) -> bool:
        """
            Determina se o dataset_id configurado no ambiente local será default.
            Ambiente CLOUD não há configuração pois sempre rodará default.
        """
        return True if self.dataset_id == self.config.default_dataset_test else False

    def _run(self) -> bool:
        """
            Função que retorna de settings se a query do artefato
            será executada.

            Se o ambiente for CLOUD, o artefato é obrigatoriamente executada.
            Se o ambiente for LOCAL, o artefato pode ou não ser executada.
        """
        return True if not self.local else params.__CLI__.run

    def _sch(self) -> bool:
        """
            Função que retorna de settings se o schema de tabelas devem
            ser carregadas online ou offline.

            Se o ambiente for CLOUD, obrigatoriamente deve-se usar online.
            Se o ambiente for LOCAL, o artefato pode ser online ou offline.
        """
        return True if not self.local else params.__CLI__.schema

    def _wlst(self) -> bool:
        """
            Função que retorna de settings se as wordlists devem
            ser carregadas online ou offline.

            Se o ambiente for CLOUD, obrigatoriamente deve-se usar online.
            Se o ambiente for LOCAL, o artefato pode ser online ou offline.
        """
        return True if not self.local else params.__CLI__.wlst

    def _plt(self) -> bool:
        """
            Função que retorna de settings se a Plotagem de
            Gráfico deve ser montada e exportada.

            Se o ambiente for CLOUD, a rotina é proibilida de plotar.
            Se o ambiente for LOCAL, a rotina pode ou não plotar.
        """
        return True if not self.local else params.__CLI__.plt

    def _dtq(self) -> bool:
        """
            Função que retorna de settings se as métricas
            para DataQuality devem ser executadas.

            Se o ambiente for CLOUD, a rotina é proibilida de executar.
            Se o ambiente for LOCAL, a rotina pode ou não executar.
        """
        return True if not self.local else params.__CLI__.dtq           


def temp_file_exists() -> None:
    """
        Rotina que verifica se já existe um arquivo na pasta temp com o nome de algum dataset e exclui o dataset.
    """
    path_file = PurePath('./tests/tmp/datasets/')
    
    if os.path.exists(path_file):
        files = os.listdir(path_file)
        for file in files:
            if file.endswith('.txt'):
                temp_file = os.path.join(path_file, file)
                with open(temp_file, 'r') as f:
                    dataset_id = f.read()
                    Governance().check_dataset_name(dataset_id)
                    if params.__HELPER__.dataset_id != dataset_id:
                        Client().drop_dataset(dataset_id)
                        f.close()
                        temp_file_deleted()


def temp_file_create() -> None:
    """
        Rotina que cria um arquivo na pasta temp com o nome do dataset configurado no settings.
    """

    name_dataset = params.__HELPER__.dataset_id
    if params.__HELPER__.config.default_dataset_test != name_dataset:
        path_file = PurePath('./tests/tmp/datasets')

        val.write_file(
            content=name_dataset,
            ext='txt',
            file=name_dataset,
            path=path_file
        )


def temp_file_deleted() -> None:
    """
        Rotina que deleta o arquivo com o nome do dataset do settings.
    """

    path_file = PurePath('./tests/tmp/datasets/')
    files = os.listdir(path_file)
    for file in files:
        if file.endswith('.txt'):
            temp_file = os.path.join(path_file, file)
            os.remove(temp_file)
