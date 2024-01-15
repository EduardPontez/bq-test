"""
  Mnemonic script GDDL Default Values
"""

__MNEMONIC_GDDL_DATASET__ = 'ds'
__MNEMONIC_LIB_IDENTIFIER__ = 'mock'    

class Governance:
  """
    Classe de Controle para validação de Padrão e Normas para Nomenclatura 
    de objetos do Data Lake gerados pela biblioteca de testes automatizados.
  """
  
  def check_dataset_name(cls, dataset:str) -> None:
    """
      Método que determina se o dataset informado pode ser gerado pela 
      rotina de testes através da API do BigQuery.
    """
    
    rule = f'{__MNEMONIC_GDDL_DATASET__}_{__MNEMONIC_LIB_IDENTIFIER__}'
    if not dataset.startswith(rule):
        raise Exception(f"""{dataset} is an invalid name. You should start using {rule}""")
