
#import pandas as pd
#from tests.resource.helpers import params
#from tests.resource.utils.logger import logger
#from tests.resource.api import wordlist as wlst

#from tests.resource.utils import validator as val

# df_rule = pd.DataFrame()
# df_procedure = pd.DataFrame()
# df_nto = pd.DataFrame()
# df_brand = pd.DataFrame()
# df_system = pd.DataFrame()
# df_propername = pd.DataFrame()
# df_attendance = list()
# df_mnemonic = list()


# def rule(rule_id: str) -> dict:
#     """
#         Função que resgata informações do wordlist_rules 
#         e devolve em formato JSON pela conversão da query
#         da própria funcionalidade do BigQuery.
#     """
#     try:
#         global df_rule
        
#         # Carrega uma única vez na memória o DataFrame
#         if df_rule.empty:
#             if params.__HELPER__.local:
#                 df_rule = metadata()
#                 logger.info('Loaded offline metadata.yaml')
#             else:
#                 df_rule = wlst.get_rules()

#         chosen = df_rule.loc[(df_rule['rule_id'] == rule_id.upper())].to_dict('records')[0]

#     except IndexError:
#         raise Exception(f'Rule_id not recognized. Got {rule_id}')

#     return chosen


# def procedure(id_procedure: int) -> dict:
#     """
#         Retorna dicionário com o nome do exame, unidade de medição e ID
#         de acordo com o ID do exame.
#     """

#     global df_procedure
#     if df_procedure.empty:
#         df_procedure = wlst.get_procedures()

#     try:
#         chosen = df_procedure[df_procedure['id_procedure'] == id_procedure]
#         cleanup = chosen.replace({np.nan: None}).to_dict('records')[0]

#     except IndexError:
#         raise IndexError(f'The following id_procedure does not exist: {id_procedure}')

#     return cleanup


# def nto() -> dict:
#     """
#         Retorna dicionário com ID e descrição do Núcleo Técnico Operacional (NTO) de maneira aleatória.
#     """

#     global df_nto
#     if df_nto.empty:
#         df_nto = wlst.get_ntos()

#     chosen = df_nto.sample().to_dict('records')[0]

#     return chosen


# def brand(mode: str) -> dict:
#     """
#         Retorna dicionário com escolha aleatória para brand, seu nome e descrição.
#     """

#     global df_brand
#     if df_brand.empty:
#         df_brand = wlst.get_brands()

#     chosen = df_brand[df_brand['fato_type'] == mode].sample().to_dict('records')[0]
#     return chosen


# def propername() -> str:
#     """
#         Retorna um nome completo de pessoa física.

#         Forename é filtrado no Pandas pelo gênero.

#         Surname é pode ser composto por 2 ou 3 nomes
#         com 90% de chances para sobrenomes comuns (COM)
#         e 10% de chances para nomes estrangeiros (FOR)
#     """

#     global df_propername

#     if df_propername.empty:
#         df_propername = wlst.get_propernames()

#     length = random.randint(2, 3)
#     middlenames = []

#     forename = df_propername.loc[df_propername['gender'] == gender(), 'name'].sample(n=1).iloc[0]

#     for _ in range(0, length):
#         typer = np.random.choice(['COM', 'FOR'], size=1, p=[0.90, 0.10]).item()
#         middlename = df_propername.loc[df_propername['gender'] == typer, 'name'].sample(n=1).iloc[0]
#         middlenames.append(middlename)

#     surname = ' '.join(name for name in middlenames)

#     return f'{forename} {surname}'.upper()


# def metadata() -> pd.DataFrame:
#     """
#         Função que retorna em formato de DataFrame o YAML 
#         de Metadata das regras com o objetivode substituir 
#         o uso da API do GCloud para execuções locais.
#     """

#     data = val.read_file(dir='./hi_automation_utils/metadata.yaml')

#     for key, value in data.items():
#         value['rule_id'] = key
#         data[key] = value

#     return pd.DataFrame(data.values())


# def mnemonic():

#     global df_mnemonic
#     if not df_mnemonic:
#         df_mnemonic = wlst.tb_hi_vacinas().to_dict('records')

#     return df_mnemonic[0]    

