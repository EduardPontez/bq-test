"""
    Script responsável por obter a classe que lê o resultado esperado
    e o resultado obtido para auxiliar nas asserções.
"""

from tests.resource.helpers import artefact
import pandas as pd

class Expected:
    """
        Classe recebe variável global de actions obtendo
        a instância do mock.
    """

    def __init__(self, **kwargs):
        self.field_name = self._field_name(**kwargs)
        self.field_value = self._field_value(**kwargs)
    
    def _field_name(self, **kwargs):
        return kwargs.get('field')
    
    def _field_value(self, **kwargs):
        return kwargs.get('value')    
    

class Obtained:

    def __init__(self, **kwargs):
        self.obtain = kwargs.get('field')

    @property
    def payload(self):
        """
            Dataframe da variável global do resultado do artefato gerado.
        """
        return pd.DataFrame(artefact.result)

    @property
    def length(self) -> int:
        """
            Retorna o total de linhas do payload do resultado.
        """
        return len(self.payload.index)

    @property
    def field(self) -> list:
        """
            Obtém a coluna do campo do payload resgatado.
        """

        # TODO : Necessário correção futura para tratar o filtro
        # de valid_record pois não está genérico. É possível que
        # esta informação esteja no arquivo config.yaml, pois não
        # filtrar o valid_record pode ocasionar em falsos positivos
        # para outros testes.

        obtained = dict()

        if self.length > 0:
            if self.obtain == 'valid_record':
                obtained = self.payload
            else:
                obtained = self.payload.query('valid_record == True')

        return list(obtained.get(self.obtain, []))

class Spy():
    """
        Classe responsável por obter as instâncias de dados
        do resultado resperado e resultado obtido.
    """

    def __init__(self, **kwargs):
        self.expected = Expected(**kwargs)
        self.obtained = Obtained(**kwargs)
