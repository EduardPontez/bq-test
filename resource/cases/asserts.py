"""
    Script responsável pela montagem da lógica dos testes unitários.
    Utiliza a classe Spy para obter valores serializados dos resultados
    esperados e obtidos.
"""

from tests.resource.cases.spy import Spy
from tests.resource.cases import utils
from datetime import datetime
import pandas as pd

def should_be_in_sequence(self, **kwargs):
    """
        Asserção de teste para valores em sequência do campo especificado.
    """

    spy = Spy(**kwargs)

    self.expected = spy.expected.field_value
    self.obtained = spy.obtained.field
    
    self().assertListEqual(self.expected, self.obtained, msg='Field does not match expected values.')

def should_be_distinct(self, **kwargs):
    """
        Asserção de teste para valores únicos do campo especificado.
    """
    
    spy = Spy(**kwargs)

    self.expected = len(spy.obtained.field)
    self.obtained = len(set(spy.obtained.field))

    self().assertEqual(self.expected, self.obtained, msg='Field does not have unique values.')

def should_not_have_datetime_before(self, **kwargs):
    """
        Asserção de teste para valores de data inicial do resultado obtido.
    """

    spy = Spy(**kwargs)
    pattern = '%Y-%m-%d %H:%M:%S'

    try:
        expected = spy.expected.field_value

        # retira espaços antes e depois da data.
        expected_strip = expected.strip()
        
        # converte a data de string para datetime.
        expected_datetime = datetime.strptime(expected_strip, pattern)
        
        # cria dataframe
        df = pd.Series(spy.obtained.field, dtype="object")
        
        # valida se o payload esta vazio para tratar o dataframe
        if len(df) > 0:           
            # converte em datetime
            df_data = pd.to_datetime(df, format='%Y-%m-%dT%H:%M:%SZ')

            # ordena e reseta o index da coluna
            df_sort = df_data.sort_values().reset_index()

            # resgata o primeito item do dataframe que é a data mais antiga
            df_obtained = df_sort.iloc[0][0]

            # formata a data em datetime
            obtained = datetime.strptime(str(df_obtained), pattern)
            
            self.obtained = obtained
            self.expected = expected_datetime
            
            self().assertLessEqual(self.expected, self.obtained, msg='Expected datetime is not Less or Equal than Obtained datetime')
        else:
            self.obtained = ''
            self.expected = expected_datetime   
            pass

    except (ValueError, TypeError, AttributeError):
        self.obtained = spy.obtained.field
        self.expected = expected
        self().fail(msg= "Invalid expected datetime, please inform in format: YYYY-MM-DD HH-MM-SS")

def should_have_on_array_length_sequence(self, **kwargs):
    """
        Asserção de teste para contagem de objetos array na sequência.
    """

    spy = Spy(**kwargs)

    self.expected = spy.expected.field_value
    self.obtained = utils.perform_array_column_to_count(df=spy.obtained.payload, field=spy.expected.field_name)

    self().assertListEqual(self.expected, self.obtained, msg='Field does not match expected length counts.')
