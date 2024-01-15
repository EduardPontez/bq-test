from tests.resource.utils import validator as val
from tests.resource.utils.logger import logger
from tests.resource.api.client import Client
from tests.resource.helpers import params
from tests import home
import json


result = None

class Artefact:
    """
        Classe responsável por ler a query e o YAML de configuração
        para realizar tratativas das tags.
    """

    def __init__(self, helper=None, replacer:bool=True):
        self.folder = None
        self.helper = self._helper(helper)
        self.location = self._location()
        self.yaml = self._yaml()
        self.pipeline = self._pipeline()
        self.destination = self._destination()
        self.query = self._query()
        self.replace = self._replace(replacer)
        self.table_ids = self._table_ids()
        self.persist = self._persist()
        self.dependencies = self._dependencies()

    def _helper(self, helper):

        if helper is None:
            return params.__HELPER__
        return helper

    def _location(self) -> str:
        """
            Retorna a concatenação do do project_id e dataset_id
            configurados na rotina para realizar as tratativas
            no artefato.
        """
        if self.helper:
            return f'{self.helper.project_id}.{self.helper.dataset_id}'

    def _yaml(self) -> dict:
        """
            Determina qual arquivo yaml serve para o rule_id
            e carrega o YAML correspondente.
        """

        target = f"{home}/{self.helper.config.pipeline_file}"
        self.folder = target.split('/')[-2]
        return val.read_file(target)

    def _pipeline(self) -> dict:
        """
            Carrega o pipeline do YAML de acordo com a regra em teste
        """
        
        try:
            return self.yaml['pipelines'][self.helper.config.pipeline_name]['parameters']['args_operator']
        except KeyError:
            return None

    def _query(self) -> str:
        """
            Obtém no YAML de configuração o path para o arquivo .sql 
            correspondente à regra. Realiza o replace das tags do 
            padrão das queries pelos valores presentes no pipeline
            da regra.
        """

        return val.read_file(dir=f"{home}/{self.folder}/{self.pipeline['BigQueryOperator']['sql']}")

    def _table_ids(self) -> list:
        """
            Retorna lista de table_ids encontrados no arquivo de artefato de teste.
        """
        return val.get_table_ids(content=self.query)

    def _replace(self, replacer: bool) -> None:
        """
            :param: replacer -> Indica a query terá substituições
            extras.
        """
        # Replace de cada parâmetro no YAML presente nas tags do script
        params = self.pipeline['BigQueryOperator']['params']
        for key, value in params.items():
            self.query = self.query.replace("${{{{{0}}}}}".format(key), str(value))

        to_replace = val.get_table_locations(content=self.query)
        
        for location in to_replace:
            self.query = self.query.replace(location, self.location)

    def _persist(self) -> list:
        """
            Persiste os table_ids determinados no arquivo de configuração da suite
            para a query a ser utilizada no teste. Os table_ids persistidos não
            trabalharão com project_id e dataset_id configurados para o teste.
        """

        # Retorna da configuração do yaml a lista de table_ids
        to_persist = self.helper.config.persist
        tables_to_persist = list()
        
        # Se a lista não for vazia, é adequado as tabelas persistidas
        if to_persist:
            
            for table_id in to_persist:
                # Obtém o nome da tabela
                table_name_from_persist = table_id.rsplit('.', 1)[-1]
                tables_to_persist.append(table_name_from_persist)
                
                # Desfaz as alterações do replace para persistir os table_ids requeridos
                self.query = self.query.replace(f'{self.location}.{table_name_from_persist}', table_id)
        
        return tables_to_persist

    def _destination(self) -> str:
        """
            Verifica o nome da tabela destino do artefato informado no arquivo de
            parameters.yaml para destination_dataset_table.
        """

        return self.pipeline['BigQueryOperator']['destination_dataset_table'].split('.')[-1]

    def _dependencies(self) -> list:
        """
            Retorna lista de nomes de tabelas encontradas no artefato de teste
            removendo ocorrências de tabelas a serem persistidas.
        """
        tables = val.get_table_names(self.table_ids)
        return [x for x in tables if x not in self.persist]


def run(artefact, mock) -> list:
    """
        Lê arquivo .sql da regra recebida e realiza execução pela a API.

        :param: mock -> Instância de Data Mock.

        Se o ambiente for Cloud, a query sempre sempre executa. Caso o 
        ambiente for Local, dependerá da configuração em settings.
    """
    global result

    if artefact.helper.run and mock:

        client = Client()
        result = list()
        
        # Sobe resultado do select da Query para tabela result
        client.insert_by_query(table_name=artefact.destination, query=artefact.query)

        logger.info('Ran Artefact Query')

        fetch = f"""
                    SELECT TO_JSON_STRING(RESULT) AS JSON
                    FROM `<<TABLE_ID>>` AS RESULT 
                    WHERE {artefact.helper.config.fetch_where} = '{eval(artefact.helper.config.fetch_search)}'
                    ORDER BY {artefact.helper.config.fetch_order};
                """

        # Retorna o resultado do Select do Artefato utilizando a conversão
        # em JSON do próprio BigQuery para tratamento mais adequado de dados
        data = client.select(query=fetch, table_name=artefact.destination, output='DICT')

        # Monta o resultado
        for row in data:
            result.append(json.loads(row['JSON']))

        if not result:
            logger.info('Query returned empty. Nothing to send')

    else:
        val.write_file(content=artefact.query, file='rendered_query', ext='sql', path='./tests/tmp')
        logger.info('Settings set to not run query')
        logger.info('Saved rendered query at ./tests/tmp')

    return result
