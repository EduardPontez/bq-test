"""
    Script responsável por interagir com a API do Google Cloud 
    para DDL (criação e deleção de tabelas) e DML (inclusão de registros)
"""

from tests.resource.utils import generator as gen
from tests.resource.utils import validator as val
from google.cloud.exceptions import NotFound
from tests.resource.helpers import params
from google.cloud import bigquery
import io

class Client:
    """    
        Classe para iniciar e encerrar conexão com API e interagir
        com elementos criados a partir das rotinas de Mock.
    """

    def __init__(self):
        self.open = None
        self.close = None
        self.usage = dict()

    def table_id(self, table_name, search='tst') -> str:
        """
            Forma o table_id a partir no nome da tabela informada e informações
            de projeto e dataset.

            :param: search -> Define se o dataset a ser usado busca em wordlists
            ou pelo dataset default onde:

            - wlt -> Referência para tabelas de wordlist
            - log -> Log (resultado teste ou falha de execução)
            - mtd -> Referência para tabela metadata
            - tst -> Referência para tabelas de teste
        """

        ids = {
            'wlt': f'{params.__HELPER__.project_id}.{params.__HELPER__.dataset_utils}.{table_name}',
            'log': f'{params.__HELPER__.project_id}.{params.__HELPER__.dataset_logs}.{table_name}',
            'mtd': f'{params.__HELPER__.project_id_mtd}.{params.__HELPER__.dataset_mtd}.{table_name}',
            'tst': f'{params.__HELPER__.project_id}.{params.__HELPER__.dataset_id}.{table_name}'
        }

        return ids.get(search)

    def _open(self) -> None:
        """
            Abre uma nova conexão com o client da API do GCloud.
        """

        if not self.open:
            self.open = bigquery.Client(project=params.__HELPER__.project_id)

    def _close(self) -> None:
        """
           Encerra a conexão aberta com o client da API do Gloud.
        """        
        if self.open:
            self.open.close()
            self.open = None

    def select(self, query: str, output: str, replacer: bool = True, table_name: str = None, search: str = 'tst'):
        """
            Retorna o select a partir de uma dada tabela e query em formato de 
            dataframe ou dicionário.

            :param: query -> Query a ser executada pela API.
            :param: output -> Determina o retorno em DF ou DICT.
            :param: replacer -> Determina se o alias para table_id deve ser substituído.
            :param: table_name -> Nome da tabela de destino em que a query será apontada.
            :param: search -> Determina se a pesquisa será para teste ou wordlists.
        """
        result = None
        # Faz replace da query recebida para setar o table_id

        if replacer:
            query = query.replace('<<TABLE_ID>>', self.table_id(table_name, search))
        self._open()

        job = self.open.query(query)
        # Recebe o e-mail do usuário que executou o job e grava na variável __USER_EMAIL__
        params.__USER_EMAIL__ = job.user_email
        # Determina o tipo de output requerido pelo retorno da API.
        if output == 'DF':
            result = job.result().to_dataframe()
        elif output == 'DICT':
            result = job.to_dataframe().to_dict('records')
        self._close()
        return result

    def insert_by_json(self, data, table_name: str, search: str = 'tst', disposition: str = 'WRITE_APPEND') -> None:
        """
            Realiza o insert de um conjunto de registros no BigQuery através de um dado
            nome de tabela e payload.
            
            :param: data -> Dados a serem enviados para o BigQuery.
            :param: table_name -> Nome da tabela alvo que receberá os registros.
            :param: search -> Referência da origem de Dataset para construção do table_id.
            :param: disposition -> Forma de escrito dos dados para a tabela de destino.
        """

        self._open()

        payload = val.get_readable_payload(data)
        table_id = self.table_id(table_name, search)
        
        try:
            job_config = bigquery.LoadJobConfig(
                write_disposition=disposition,
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                autodetect=False,
                ignore_unknown_values=True
            )
            
            job = self.open.load_table_from_file(payload, table_id, job_config=job_config)
            job.result()
        except Exception:
            #print(job.errors)
            raise Exception(f'Cannot send Data Mock. Target "{table_id}" is unavailable.')

        self._close()

    def insert_by_query(self, table_name: str, query: str, disposition: str = 'WRITE_TRUNCATE') -> None:
        """
            Inicia um JOB no BigQuery para carregar registros em Write Append
            através de um statement prévio.
            
            :param: table_name -> Nome da tabela de destino do JOB.
            :param: query -> Query a ser executada (não sofrerá replace e deve conter table_id).
            :param: disposition -> Forma de escrito dos dados para a tabela de destino.
        """

        self._open()

        try:
            # Cria um Job Config com a tabela de destino informada.
            job_config = bigquery.QueryJobConfig(
                use_legacy_sql=False,
                write_disposition=disposition,
                destination=self.table_id(table_name)
            )

            # Executa o Job.
            job = self.open.query(query, job_config=job_config)
            job.result()
            del job
        except Exception:
            raise Exception(f'Cannot send Data Mock. Target "{table_name}" is unavailable.')

        self._close()

    def create_dataset(self, dataset_id: str = None) -> None:
        """
            Cria um dado dataset_id de acordo com o valor recebido.
        """         
        self._open()

        if dataset_id:
            params.__HELPER__.dataset_id = dataset_id

        if not self.is_dataset(params.__HELPER__.dataset_id):
            dataset = bigquery.Dataset(f'{params.__HELPER__.project_id}.{params.__HELPER__.dataset_id}')
            self.open.create_dataset(dataset, timeout=30, exists_ok=True)

        self._close()   

    def drop_dataset(self, dataset_id: str = None) -> None:
        """
            Remove um dado dataset_id de acordo com valor recebido.

            :param: dataset_id -> Objeto do tipo Classe BigQuery.
        """

        self._open()
        
        # if dataset_id:
        #     params.__HELPER__.dataset_id = dataset_id

        self.open.delete_dataset(
            # dataset=params.__HELPER__.dataset_id, 
            dataset=dataset_id,
            delete_contents=True, 
            not_found_ok=True
        )
              
        self._close()

    def create_table(self, table_name: str, schema: list, search: str = 'tst') -> None:
        """
            Cria uma dada table_id de acordo com o nome da tabela informada
        """        
        self._open()

        # Verifica primeiro se a tabela informada para criação já existe.
        if not self.is_table(table_name=table_name):

            table_id = bigquery.Table(self.table_id(table_name, search), schema=schema)
            self.open.create_table(table_id, exists_ok=True)
            expiration = gen.datetime_from_diff(days=3)
            table_id.expires = expiration
            self.open.update_table(table_id, ["expires"])
       
        self._close()

    def temporary_table(self, query: str) -> str:
        """
            Função que recebe uma determinada query
            e a executa no BigQuery para retornar o valor
            de temporary_table do job criado pela API.
        """

        self._open()
        destination = None
        
        try:
            job = self.open.query(query)
            job.result()
            destination = job.destination
        except Exception:
            raise Exception(f'Cannot get temporary_table')

        self._close()

        return str(destination)

    def is_table(self, table_name: str) -> bool:
        """
            Função que verifica se uma dada table_id já existe
            no ambiente do BigQuery.
        """
        try:
            self.open.get_table(self.table_id(table_name))
            return True
        except NotFound:
            return False

    def is_dataset(self, dataset_id: str) -> bool:
        """
            Função que verifica se um dado dataset_id já existe
            no ambiente do BigQuery.
        """
        try:
            self.open.get_dataset(f'{params.__HELPER__.project_id}.{dataset_id}')
            return True
        except NotFound:
            return False

    def update_usage(self, schema: list, table_name: str) -> None:
        """
            Rotina responsável por armazenar os schemas em tempo de 
            execução.
        """

        if table_name not in self.usage:
            self.usage[table_name] = schema

    def save_schema(self, schema: list, table_name: str) -> None:
        """
            Rotina que salva versão offline do schema encontrado da tabela.
        """

        self._open()

        path = './tests/tmp/schemas'
        
        f = io.StringIO("")
        self.open.schema_to_json(schema, f)
        converted = f.getvalue()

        val.write_file(
            content=converted, 
            ext='json', 
            file=table_name, 
            path=path
        )

        self._close()

    def get_offline_schema(self, main_name: str = None, table_name: str = None) -> list:
        """
            Função retorna o schema de uma tabela em formato de lista
            a partir de uma dada table_id pela Tmp Folder.
        """

        self._open()
        
        target = f'./tests/tmp/schemas/{table_name}.json'
        if val.is_recent_file(target):
            schema = self.open.schema_from_json(target)
        else:
            schema = self.get_online_schema(main_name=main_name, table_name=table_name)
        
        self.update_usage(schema=schema, table_name=table_name)
        self._close()

        return schema

    def get_online_schema(self, main_name: str = None, table_name: str = None) -> list:
        """
            Função retorna o schema de uma tabela em formato de lista
            a partir de uma dada table_id pela API do BigQuey
        """

        self._open()

        table_id = None
        schema = None
        
        if main_name is None:
            for reference in params.__HELPER__.references:
                try:
                    table_id = f'{reference}.{table_name}'
                    self.open.get_table(table_id)
                    break
                except NotFound:
                    pass
        else:
            table_id = main_name

        try:
            schema = self.open.get_table(table_id).schema
        except NotFound:
            Exception('Cannot find an existing table reference.')
        
        if params.__HELPER__.local:
            self.save_schema(schema=schema, table_name=table_name)
        
        self.update_usage(schema=schema, table_name=table_name)
        self._close()
        
        return schema

    def fetch_schema(self, main_name: str = None, table_name: str = None) -> list:
        """
            Função que determina de qual maneira o schema da tabela
            será buscada, onde:

            memory_usage -> Schemas armazenados em tempo de execução
            offline -> Consulta tmp folder
            online -> Consulta API do BigQuery
        """

        if table_name in self.usage:
            return self.usage.get(table_name)
        else:
            if params.__HELPER__.sch:
                return self.get_online_schema(main_name, table_name)
            else:
                return self.get_offline_schema(main_name, table_name)

    def get_user_email(self):
        """
            Função que retorna o e-mail do client que irá executar os jobs no bigquery
        """
        self._open()
        
        try:
            job = self.open.query("SELECT current_date()")
            params.__USER_EMAIL__ = job.user_email
        except Exception:
            raise Exception(f'Query Error')

        self._close()

