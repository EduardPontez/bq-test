"""
    Script para concetrar validações em uso para utils e api.
"""

import os
import re
import pytz
import time
from json import dumps
from io import StringIO
from yaml import safe_load
from pathlib import Path
from pathlib import PurePath
from pandas import DataFrame
from datetime import datetime
from datetime import timezone
from platform import system
from platform import release
from platform import python_version
from importlib import import_module
from tests.resource.helpers import params
from tests.resource.utils import generator as gen
from tests.resource.utils.custom import constructor_yaml

def is_date(date: str):
    """
        Verifica se uma data é válida no formato: YYY-MM-DD
    """
    pattern = '%Y-%m-%d %H:%M:%S'
    try:
        date = datetime.strptime(date, pattern)
        return date.strftime(pattern)
    except:
        try:
            now = gen.datetime_from_current(string=False)
            date = datetime.strptime(date[:10], '%Y-%m-%d')
            date = date.replace(hour=now.hour,
                                minute=now.minute,
                                second=now.second,
                                microsecond=now.microsecond)   
            return date.strftime(pattern)   
        except: 
            return False


def is_alias(alias: str):
    """
        Verifica se o base_date informado é um possível
        alias. Exemplos: Y-3, M-4, D-5
    """

    # Mesmo se o valor não estiver no fomato correto,
    # ainda verifica se a data pode ser um comando
    # (ex: Y-4, M-3, D-2)

    if re.match('^((Y|M|W|D|H|SEC|MIN)[+|-][0-9]+)+$', str(alias).upper()):
        return alias
    elif re.match('^[\d]+$', str(alias)):
        return f'D+{alias}'
    elif re.match('^-[\d]+$', str(alias)):
        return f'D{alias}'        
    return False


def is_interval_alias(alias: str):
    """
        Verifica se o base_date informado é um possível
        alias. Exemplos: Y-3, M-4, D-5
    """
    inspect = re.sub(r'[^\w+-]', '', alias)
    return True if re.match('^((Y|M|W|D|H|SEC|MIN)[+|-]\d+)+$', str(inspect).upper()) else False


def is_file(file: str) -> bool:
    """
        Função que retorna booleano para
        verificar a existência de um arquivo.
    """
    return os.path.exists(file)


def get_dir(path: str) -> None:
    """
        Método que cria um dado diretório com
        sub-pastas já identificando sua existência.
    """

    Path(PurePath(path)).mkdir(
        parents=True,
        exist_ok=True
    )


def get_operational_system() -> str:
    """
        Função que retorna o tipo de sistema operacional
        que iniciou a rotina juntamente com sua versão.
    """

    return f'{system()} {release()}'.upper()


def get_python_version() -> str:
    """
        Função que retorna qual é a versão de instalação
        do Python que iniciou a execução da rotina.
    """

    return python_version()


def get_package_version(package: str) -> str:
    """
        Função que recebe um nome de um package python
        e verifica sua instalação. 
        
        Em caso de sucesso de importação, retorna sua
        versão corrente. Em falha, retorna nulo.
    """

    try:
        module = import_module(package, package=None)
        return module.__version__
    except ModuleNotFoundError:
        return None


def get_local_timezone() -> str:
    """
        Função que verifica o GMT positivo 
        do ambiente local para cálculo de 
        diferença entre timezone local e UTC.
    """
    diff = time.timezone / 3600
    if diff == 0:
        return 'UTC'
    return f'Etc/GMT+{int(diff)}'


def get_diff_timezone(negative=False) -> int:
    """
        Função que calcula a diferença de horas
        entre o GMT local e o UTC para tratar
        comportamento do Plotly com x-axis em data

        issue: https://github.com/plotly/plotly.py/issues/3065
    """
    
    from_tz = pytz.timezone(get_local_timezone())
    to_tz = pytz.timezone('UTC')

    utc_dt = datetime.now(timezone.utc)
    dt_from = datetime.utcnow()

    dt_from = from_tz.localize(dt_from)
    dt_to = to_tz.localize(datetime.utcnow())

    from_d = dt_from - utc_dt
    if from_d.days < 0:
        return get_diff_timezone(True)

    dt_delta = dt_from - dt_to

    negative_int = -1 if negative else 1
    return int(dt_delta.seconds/3600)*negative_int


def get_readable_payload(payload) -> StringIO:
    """
        Função que converte um dado payload em
        DataFrame ou dicionário para formatação
        StringIO com compartibilidade para envio
        de payload pela API do BigQuery.
    """
    
    to_json = None

    if isinstance(payload, DataFrame):
        to_json = payload.to_json(orient='records', lines=True)
    
    elif isinstance(payload, dict):
        to_json = dumps(payload)
    # print(to_json)
    return StringIO(to_json)


def read_file(dir: str) -> str:
    """
        Função responsável por abrir arquivo YAML ou SQL e devolver
        seu conteúdo em string. 

        :param: dir -> Caminho do diretório atual para o arquivo, 
        incluindo o nome do arquivo
    """
    loaded = None
    try:
        with open(PurePath(dir), 'r', encoding='utf8') as f:
            if dir.endswith('.yaml'):
                loaded = safe_load(f)
            
            elif dir.endswith('.sql'):
                loaded = f.read()
            
            elif dir.endswith('.txt'):
                loaded = f.read()
        f.close()
    
    except FileNotFoundError:
        raise Exception(f'Cannot open YAML, SQL ou TXT file for path: {dir}')

    return loaded


def write_file(content: str, file: str, ext: str, path: str) -> None:
    """
        Método que salva valor recebido em texto
        em arquivo gravado em disco em um diretório
        ignorado pelo git.

        :param: content -> texto a ser gravado em disco
        :param: file -> Nome do arquivo
        :param: ext -> extensão do arquivo
        :param: path -> diretório do arquivo
    """
    
    get_dir(path=path)

    with open(f'{path}/{file}.{ext}', 'w', encoding='UTF-8') as f:
        f.write(content)
    f.close()


def get_table_names(table_ids: list) -> list:
    """
        Função de determina o nome de tabelas a partir de um dado
        conjunto de table_ids

        table_ids -> Lista com formatação project_id.dataset_id_table_name
    """

    table_names = list()
    
    for table_id in table_ids:
        table_name = table_id.rsplit('.', 1)[-1]
        table_names.append(table_name)
    
    # Remove da lista, tabelas que são chamadas por prefixo all
    to_clear = [table for table in table_names if '*' not in table]
    
    # Retorna lista com nomes únicos das tabelas
    return list(set(to_clear))


def get_table_locations(content: str) -> list:
    """
        A partir de uma dada query retorna lista
        de localizações de tabelas: project_id.dataset_id

        :param: -> content: query a ser analizada.
    """
    
    found = list()
    pattern = '\`(.*?)\.(.*?)\.(.*?)\`'

    p = re.compile(pattern)
    table_ids = ["%s.%s.%s" % x for x in p.findall(content)]

    for table_id in table_ids:
        found.append(table_id.rsplit('.', 1)[0])
    
    return list(set(found))


def get_table_ids(content: str) -> list:
    """
        Obtém lista de table_ids a partir de uma query.
    """

    pattern = '\`(.*?)\.(.*?)\.(.*?)\`'
    
    p = re.compile(pattern)
    table_ids = ["%s.%s.%s" % x for x in p.findall(content)]
    
    return list(set(table_ids))


def get_latest_datetime(dates: list):

    try:
        sort = sorted(dates)
        return sort[-1]
    except Exception:
        return 


def is_table_id(content: str) -> bool:
    """
        Verifica se uma dada string está em formato
        de table_id.
    """

    pattern = '(.*?)\.(.*?)\.(.*?)'
    return bool(re.fullmatch(pattern, content))

def is_recent_file(path: str = None) -> bool:
    """
        Função para retornar se o arquivo existe e a data de alteração é menor que params.__DAYS_TO_UPDATE_SCHEMA__
    """
    if is_file(path):
        last_modified = datetime.fromtimestamp(os.path.getmtime(path)).date()        
        if (datetime.now().date() - last_modified).days < params.__DAYS_TO_UPDATE_SCHEMA__: 
            return(True)      
    return(False)
  
    

