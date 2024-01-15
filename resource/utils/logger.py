"""
    Script para instanciar uma variável de escopo global na padronização
    de log ao executar rotina para criação de Data Mock.
"""

import logging

logger = logging

try:
    logger.basicConfig(
        format='[{levelname:^8s}] - {asctime} - {message}', 
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{'
    )

except:
    raise Exception('Not a valid logger settings')