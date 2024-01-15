"""
    Script responsável por criar e enviar o log de execução para Data Mock
"""

from tests.resource.utils import generator as gen
from tests.resource.utils import validator as val
from tests.resource.utils.logger import logger
from tests.resource.api.client import Client
from tests.resource.helpers import params


class LogResult:
    """
        Classe responsável por enviar o Log de execução para o Data Mock

        :param: data -> instância da clase Mocker com as informações de execução
    """

    def __init__(self, data, status: str, duration: str, units: list):
        self.suite = self._suite(data)
        self.test = self._test(data)
        self.status = self._status(status)
        self.description = self._description(data)
        self.tags = self._tags(data)
        self.execution = self._execution()
        self.duration = self._duration(duration)
        self.user = self._user()
        self.dataset = self._dataset()
        self.key = self._key(data)
        self.env = self._env()
        self.units = self._units(units)

    def _suite(self, data) -> str:
        """
            Retorna o nome da suite em teste.
        """
        return data.suite.upper()

    def _test(self, data) -> str:
        """
            Retorna o ID do teste que houve a execução para envio do Mock.
        """
        return data.testcase.upper()

    def _status(self, status) -> str:
        """
            Retorna o status do teste executado podendo assumir
            PASS, FAIL ou SKIP
        """

        return status

    def _description(self, data) -> str:
        """
            Retorna descrição do cenário de teste.
        """

        return data.documentation.get('desc')

    def _tags(self, data) -> list:
        """
            Retorna o status do teste executado podendo assumir
            PASS, FAIL ou SKIP
        """
        return data.documentation.get('tags')

    def _execution(self) -> str:
        """
            Retorna a data atual do sistema.
        """
        return gen.datetime_from_current()

    def _duration(self, duration) -> str:
        """
            retorna a duração do teste executado.
        """
        return duration

    def _user(self) -> str:
        """
            Retorna o e-mail autenticado n GCP do usuário configurado no ambiente 
            em que a rotina de Data Mock é executada. Caso o e-mail não for encontrado,
            o hostname do ambiente é retornado. 
        """        
        user = None
        try:        
            if params.__HELPER__.run == False:
                Client().get_user_email()
            user = params.__USER_EMAIL__
        except Exception:
            user = params.__HELPER__.hostname.upper()
        finally:
            if not user:
                user = params.__HELPER__.hostname.upper()

        return user

    def _dataset(self) -> str:
        """
            Retorna o nome do dataset reconhecido pelo Helper.
        """
        return params.__HELPER__.dataset_id

    def _key(self, data) -> str:
        """
            Retorna da instância do Mocker, o patient_key gerado da instância
            única do paciente incluso no teste.
        """
        return data.key.lower()

    def _env(self) -> str:
        """
            Retorna o tipo de ambiente identificado na instância do Helper
        """
        return params.__HELPER__.environment

    def _units(self, units:list) -> list:
        """
            Retorna lista resultante dos testes unitários
            com o nome do teste e resultado esperado e obtido.
        """
        return units


class LogError:

    def __init__(self, trace: dict):
        self.execution = self._execution()
        self.system = self._system()
        self.python = self._python()
        self.packages = self._packages()
        self.exception = self._exception(trace)
        self.description = self._description(trace)
        self.trace = self._trace(trace)

    def _execution(self) -> str:
        """
            Retorna a data atual do sistema.
        """
        return gen.datetime_from_current()


    def _system(self) -> str:
        """
            Retorna o sistema operacional.
        """
        return val.get_operational_system()

    def _python(self) -> str:
        """
            Retorna o sistema operacional.
        """
        return val.get_python_version()

    def _packages(self) -> str:
        """
            Função que retorna um dicionário em string com as versões
            de packages através de uma dada coleção.
        """

        found = dict()

        packages = ['attr', 'numpy', 'pandas', 'pyarrow', 'dateutil',
                    'yaml', 'google.protobuf', 'google.cloud.bigquery']

        for package in packages:
            found[package] = val.get_package_version(package)

        return str(found)

    def _exception(self, trace: dict) -> str:
        """
            Retorna o tipo de Classe de Exceção gerada
            pela execução podendo admitir error tratados
            ou não tratados.
        """

        exception = str(trace.get('exc_type', None))
        clean = exception.replace("<class '", '').replace("'>", '')
        return clean

    def _description(self, trace:dict) -> str:
        """
            Retorna a descrição do erro que acompanha
            o tipo de classe de Exceção podendo admitir
            mensagens built-in ou personalizados.
        """        

        return str(trace.get('_str', None))

    def _trace(self, trace: dict) -> str:
        """
            Retorna o 'last call traceback' do arquivo em que
            ocorreu a exceção juntamente com a linha demarcada.
        """

        return str(trace.get('stack', None))


def send(Log, target: str) -> None:
    """
        Envia para o BigQuery o Log de execução.
    """

    # Envia o log
    client = Client()
    client.insert_by_json(table_name=target, data=Log.__dict__, search='log')

    if target == 'log_result':
        logger.info('Sent test result')
        logger.info(f'Generated key {Log.key}')
        logger.info(f'Finished execution for user {Log.user}\n')
    else:
        logger.info('Sent log error\n')
