"""
    Módulo responsável por carregar o arquivo de configuração
    da suite (config.yaml).
"""

from tests.resource.utils import validator as val
from tests.resource.utils.governance import Governance

class SuiteConfig:
    """
        Classe responsável por carregar os parâmetros
        informados no config.yaml para preparar a execução
        dos cenários.

        :path: -> Diretório da suite de teste.
    """
    def __init__(self, path:str): 
        
        self.yaml =self._yaml(path)
        self.pipeline_file = self._pipeline_file()
        self.pipeline_name = self._pipeline_name()
        self.persist = self._persist()
        self.fetch_search = self._fetch_search()
        self.fetch_where = self._fetch_where()
        self.fetch_order = self._fetch_order()
        self.default_dataset_test = self._default_dataset_test()
    
    def _yaml(self, path:str) -> dict:
        """
            Retorna dicionário carregado a partir do arquivo
            config.yaml da suite.

            :path: -> Diretório da suite de teste.
        """
        if path:
            target = path.replace('test.yaml', 'config.yaml')
            return val.read_file(dir=target)
        else:
            return dict()
    
    def _pipeline_file(self) -> str:
        """
            Retorna o diretório do arquivo de parâmetros da DAG.
        """
        try:
            return self.yaml['query']['location']['pipeline_file']
        except KeyError:
            pass
        

    def _pipeline_name(self) -> str:
        """
            Retorna o nome do pipeline do arquivo de parâmetros
            da DAG que correspondente a suite de teste.
        """
        try:
            return self.yaml['query']['location']['pipeline_name']
        except KeyError:
            pass
        
    def _persist(self) -> list:
        """
            Retorna lista de table_ids a serem persistidos na
            query. Como o parâmetro é opcional no arquivo config.yaml,
            é retornado lista vazia caso não informado.
        """
        
        try:
            return self.yaml['query']['persist']
        except KeyError:
            return list()

    def _fetch_search(self) -> str:
        """
            Retorna chave de pesquisa do mock a ser utilizada
            para obter os resultados obtidos no artefato de teste.
        """
        
        try:
            return self.yaml['query']['fetch']['search']
        except KeyError:
            pass

    def _fetch_where(self) -> str:
        """
            Retorna a coluna a ser utilizada para o filtro do
            fetch_search na obtenção do resultado obtido gerado
            pelo artefato de teste.
        """
        try:
            return self.yaml['query']['fetch']['where']
        except KeyError:
            pass
        
    def _fetch_order(self) -> str:
        """
            Retorna a coluna a ser utilizada para ordenação dos
            resultados obtidos do artefato de teste.
        """
        try:
            return self.yaml['query']['fetch']['order']
        except KeyError:
            pass

    def _default_dataset_test(self) -> str:
        """
            Retorna o valor default para o dataset da suite
            informado no arquivo config.yaml
        """
        try:
            default = self.yaml['environment']['default_dataset_test']
            Governance().check_dataset_name(default)
            return default
        except KeyError:
            pass
