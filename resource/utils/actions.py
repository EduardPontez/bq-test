"""
    Script responsável por particionar as responsabilidades na preparação do ambiente
    do BigQuery para a execução de cenários de teste.
"""


from tests.resource.api.client import Client
from tests.resource.utils import dataquality
from tests.resource.helpers import artefact
from tests.resource.helpers import helper
from tests.resource.helpers import params
from tests.resource.utils import mocker
from tests.resource.utils import graph
from tests.resource.api import events
from tests.resource.api import logger


mock = None
config = None
evidence = None
testware = None


def setUpClass(path: str, suite: str, testcase: str):

    """
        Trecho responsável por verificar o ambiente de teste, preparar e executar o 
        envio do Mock para os módulos de teste.
    """
    global mock
    global config
    global evidence
    global testware

    # Inicializa configurações de ambiente
    params.__HELPER__ = helper.Helper(path=path, suite=suite, testcase=testcase)

    # Executa a rotina de validação do arquivo temp_file.
    helper.temp_file_exists()

    # Executa a rotina de criação do arquivo temp_file.
    helper.temp_file_create()

    # Carrega o Artefato de Teste
    testware = artefact.Artefact()

    # Carrega o Data Mock
    mock = mocker.build(path=path, suite=suite, testcase=testcase)

    # Cria dataset e tabelas dependentes para a query
    events.create_artefact_objects(artefact=testware)
    
    # Envia Data Mock
    events.mockup_to_bigquery(mock=mock.events)

    # Executa a Query correspondente
    evidence = artefact.run(artefact=testware, mock=mock)


def tearDownClass(status: str, duration: str, units: list):
    
    global mock
    global evidence

    # Valida o dataset configurado e argumento de persistência para expurgo.
    if not params.__HELPER__.default and not params.__CLI__.persist_dataset:
        
        dataset_id = params.__HELPER__.dataset_id
        Client().drop_dataset(dataset_id)
        helper.temp_file_deleted()

    # Plota gráfico para cenário correspondente
    graph.build(mock, evidence)

    # Envia Log de Execução para o Data Mock criado
    log = logger.LogResult(
        data=mock, 
        duration=duration, 
        status=status,
        units=units
    )

    logger.send(log, target='log_result')
