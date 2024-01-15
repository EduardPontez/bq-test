"""
    Script responsável por determinar os Actions para eventos
    em setUp dos Cenários de Teste com a API do GCloud.
"""

from tests.resource.utils.logger import logger
from tests.resource.api.client import Client
from tests.resource.helpers import params


client = Client()


def reset_dataset() -> None:
    """
        Rotina responsável por dropar e criar novamente
        o dataset_id a ser utilizado para upload de mock.
    """
    
    global client

    if not params.__HELPER__.default:
        dataset_id = params.__HELPER__.dataset_id
        client.drop_dataset(dataset_id)
        logger.info(f'Reseted Dataset {params.__HELPER__.dataset_id}')
    else:
        logger.info(f'Using default dataset {params.__HELPER__.dataset_id}')

    client.create_dataset()


def create_artefact_objects(artefact) -> None:
    """
        Método responsável por criar tabelas dependentes para
        funcionamento da query.
    """

    global client

    reset_dataset()

    # Para cada tabela dependente da regra é definido o schema adequado para criação
    for table_name in artefact.dependencies:
        schema = client.fetch_schema(table_name=table_name)
        client.create_table(table_name=table_name, schema=schema)

    if not params.__HELPER__.default:
        logger.info('Created required tables')


def mockup_to_bigquery(mock: dict) -> None:
    """
        Rotina responsável por enviar o Data Mock ao BigQuery
        agrupado por tabela.
    """
    
    global client

    for dataframe in mock.values():

        if dataframe is not None:
            
            dataframe.reset_index(drop=True, inplace=True)
            
            for table_name, df_group in dataframe.groupby('table_name', sort=False):
                
                main_name = df_group['main_name'].iloc[0]
                schema = client.fetch_schema(main_name=main_name, table_name=table_name)
                
                client.create_table(table_name=table_name, schema=schema)
                client.insert_by_json(table_name=table_name, data=df_group)

                logger.info(f'{len(df_group.index)} row(s) sent to {table_name}')
