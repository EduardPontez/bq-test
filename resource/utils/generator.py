"""
    Script utilizado para gerar massa de dados de informações que não
    são passadas manualmente e preenchem valores para camadas superiores
    com suas respectivas regras de criação para evitar informações nulas.
"""

import re
import uuid
import string
import random
import hashlib
import numpy as np
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta

def gender() -> str:
    """
        Retorna dois valores possíveis para gênero:
        M ou F com 50% de chances para cada um.
    """

    return np.random.choice(['M', 'F'], size=1, p=[.5, .5]).item()


def attendance():

    global df_attendance
    if not df_attendance:
        df_attendance = wlst.idd_bi_dm_hospital_patient_attendance().to_dict('records')

    return df_attendance[0]

def datetime_from_current(string: bool = True) -> str:
    """
        Retorna o horário atual do sistema em datetime.
    """

    date = datetime.utcnow()

    if string:
        return date.strftime('%Y-%m-%d %H:%M:%S')
    return date    


def birthdate_from_age(age: int, base: str) -> str:
    """
        Função para retornar uma data de nascimento através do
        da informação de idade recebida.
    """

    # start_date = date.today() - relativedelta(years=age, days=364)
    base = datetime.strptime(base[:10], '%Y-%m-%d')

    start_date = base - relativedelta(years=age + 1)
    chosen_date = start_date + relativedelta(days=360)

    return chosen_date.strftime('%Y-%m-%d')


def age_from_birth_date(birth_date: str, base_date: str) -> int:
    """
        Função que determina a quantidade de idade em anos a partir
        de uma data de referência e a data de nascimento.

        :param: base_date -> Data de referência para data atual
        :param: birth_date -> Data de nascimento para subtração da data base
    """

    today = datetime.strptime(base_date[:10], '%Y-%m-%d')

    birth_date_to_datetime = datetime.strptime(birth_date, '%Y-%m-%d')

    age = today.year - birth_date_to_datetime.year - ((today.month, today.day) < \
          (birth_date_to_datetime.month, birth_date_to_datetime.day))

    return age


def datetime_from_diff(days: int) -> datetime:
    """
        Função que retorna uma data futura a partir da
        data atual do sistema com o total de dias informado.

        :param: days -> Dias a serem somados na data corrente.
    """
    return datetime_from_current(string=False) + timedelta(days=days)


def idcode(numeric: bool = True, length: int = 0, sep: str = '', min_value = 1000000000, max_value = 9999999999):
    """
        Retorna um ID com total de dígitos personalizados preservando zeros à esquerda

        :param: numeric ->
        Se False retorna ID em string
        Se True retorna ID em inteiro

        :param: length ->
        Determina o total de dígitos do ID. Se não informado retorna comprimento de 10 dígitos
    """

    if length != 0:
        min_value = 1
        max_value = (10 ** length) - 1

    # Máscara para preservar leading zeros
    chosen = f'%0{length}d' % random.randint(min_value, max_value)

    if not numeric:
        return f'{chosen[:-1]}{sep}{chosen[-1:]}'
    return int(chosen)


def cpf(formatting: bool = False) -> str:
    """
        Retorna um CPF válido de acordo com a regra
        de formação estabelecida pela Receita Federal

        :param formatting ->
        Se False retorna CPF sem máscara
        Se True retorna CPF com máscara

        source: https://gist.github.com/lucascnr/24c70409908a31ad253f97f9dd4c6b7c
    """

    _cpf = [random.randint(0, 9) for _ in range(9)]

    for _ in range(2):
        val = sum([(len(_cpf) + 1 - i) * v for i, v in enumerate(_cpf)]) % 11

        _cpf.append(11 - val if val > 1 else 0)

    if formatting:
        return '%s%s%s.%s%s%s.%s%s%s-%s%s' % tuple(_cpf)
    else:
        return '%s%s%s%s%s%s%s%s%s%s%s' % tuple(_cpf)


def uf() -> str:

    uf.choices = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT',
           'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO',
           'RR', 'SC', 'SP', 'SE', 'TO']

    return random.choice(uf.choices)


def crm() -> str:
    """
        Retorna registro fictício para Conselho Regional de Medicina
        em 15 caracteres.
    """

    uf()
    choices = uf.choices

    number = '%08d' % random.randint(0, 99999999)
    _crm = f'CRM-{random.choice(choices)}-{number}'

    return _crm


def hashcode(value: str, mode: str) -> str:
    """
    Retorna um dado valor codificado para SHA1 ou SHA256

    :param: value -> valor em string para conversão.
    :param: mode -> formato de transformação (SHA1 ou SHA256)
    """

    if mode.upper() == 'SHA1':
        return hashlib.sha1(value.encode('utf-8')).hexdigest()
    elif mode.upper() == 'SHA256':
        return hashlib.sha256(value.encode('utf-8')).hexdigest()


def identifier() -> str:
    """
        Função que gera um identificador único
        utilizando lib built-in uuid na versão 4.
    """
    return str(uuid.uuid4())


def boolean(string: bool = False) -> bool:
    """
        Função que retorna um valor booleano
        pseudo-aleatório.
    """

    chosen = random.choice([True, False])
    return chosen if not string else str(chosen)


def choice(variance: list) -> str:
    """
        Função que recebe uma lista e escolhe
        um dos elementos para retorno.
    """
    return random.choice(variance)


def percentual(string: bool = False, decimals: int = 5, max: int = 5) -> float:
    """
        Função que retorna um valor float determinando a quantidade
        de casas decimais e o maior valor para geração.
    """

    chosen = random.uniform(0, max)
    rounds = round(chosen, decimals)
    return rounds if not string else str(rounds)


def accession_number() -> str:
    """
        Função usada para criar número de accession number usada pela
        classe da fato_producao_exame_rdi.
    """

    def digit(digits):
        return f'%0{digits}d' % random.randint(0, 9)

    def letter():
        return f'{random.choice(string.ascii_uppercase)}'

    chosen = list()
    chosen.append(digit(3))
    chosen.append(letter())
    chosen.append(letter())
    chosen.append(digit(1))
    chosen.append(letter())
    chosen.append(letter())
    chosen.append(digit(3))
    chosen.append(digit(1))
    chosen.append(digit(1))
    chosen.append(letter())

    return ''.join(chosen)


def alias_date(alias: str, keep_hms=True, start_date: str = None, debit: int = None):
    """
        Determina um base_date de acordo com alias estabelecido.
        Exemplos:
        Y-5 -> base_date será 5 anos atrás a partir de hoje
        M-2 -> base_date será 2 meses atrás a partir de hoje
        W-3 -> base_date será 3 semanas atrás a partir de hoje
        D-7 -> base_date será 7 dias atrás a partir de hoje
        H-1 -> base_date será 1 hora atrás a partir de hoje
        MIN-35 -> base_date será 35 minutos atrás a partir de hoje
        SEC-12 -> base_date será 12 segundos atrás a partir de hoje
    """

    if not start_date:
        start_date = datetime_from_current(string=False)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

    alias = alias.replace(' ', '')
    template = re.split("([+-])", alias)

    sched = {
        'unity': template[0].upper(),
        'operator': template[1],
        'interval': int(template[-1])
    }

    rel = {
        'Y': relativedelta(years=sched['interval']),
        'M': relativedelta(months=sched['interval']),
        'W': relativedelta(weeks=sched['interval']),
        'D': relativedelta(days=sched['interval']),
        'H': relativedelta(hours=sched['interval']),
        'MIN': relativedelta(minutes=sched['interval']),
        'SEC': relativedelta(seconds=sched['interval'])
    }

    interval = rel.get(sched['unity'])

    if sched['operator'] == '-':
        diff = start_date - interval
    else:
        diff = start_date + interval

    if debit:
        diff = diff - relativedelta(days=debit)

    to_timestamp = datetime.timestamp(diff)
    to_datetime = datetime.fromtimestamp(to_timestamp)

    if keep_hms:
        to_datetime = to_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    final_date = to_datetime.strftime('%Y-%m-%d %H:%M:%S')

    return final_date
