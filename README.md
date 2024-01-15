# Bq-test

Projeto criado para criar testes automatizados com base no retorno de execução de query em ambiente de **BigQuery**. Crie Mock de Dados para linhas em tabelas e teste a asserção dos resultados obtidos com esperados.

# Requirements

Necessário instalação e configuração do Google Cloud SDK:
https://cloud.google.com/sdk/docs/install?hl=pt-br

## Sample

```yaml
My_First_Test:

  documentation:
    tags: [principal_test, select_test]
    desc: >
      Given my table test with 2 rows
      When I run my query
      Then I must assert select result in unittests.

  unittests:
    my_string_should_be_in_sequence: [test_1, test_2]
    my_integer_should_be_in_sequence: [1, 2]
    my_string_date_should_be_distinct: ~
    identification_date_should_not_have_datetime_before: "2018-01-01 00:00:00"

  settings:
    base_date: Y-1 #2023-14-01

  mockup:
    - project.dataset.table:
        my_string: test_1
        my_date_datetime: D + 1
        my_integer: 1

    - project.dataset.table:
        my_string: test_2
        my_date_datetime: D + 2 *
        my_integer: 2
```

![image](https://github.com/EduardPontez/bq-test/assets/35925620/4971c64c-6863-4798-925f-47f1f8900af6)

## Yaml

### `documentation`

- **tags**: Tags para cenário.
- **desc**: Descrição geral do teste.

### `unittests`

- **column_should_be_in_sequence**: Asserção sequencial a partir do nome de uma coluna informada como prefixo.
- **column_should_be_distinct**: Asserção para determinar se todos os valores de uma coluna informada como prefixo é única.
- **column_should_not_have_datetime_before**: Asserção que define uma data mínima para a identificação de datas.

### `settings`

- **base_date**: Marco zero temporal para uso em campos de data no formato alias ou yyy-mm-dd.

### `mockup`

- **project.dataset.table**: Define um mockup (simulação) para a tabela especificada. Inclui valores simulados para as colunas. Exemplo:
  - `my_string`: test_1.
  - `my_date_datetime`: Data simulada D + 1.
  - `my_integer`: Valor inteiro simulado 1.

## Scheduler

| Alias           | Desc                        |
| --------------- | --------------------------- |
| SEC             | Segundo                     |
| MIN             | Minuto                      |
| H               | Hora                        |
| D               | Dia                         |
| W               | Semana                      |
| M               | Mês                         |
| Y               | Ano                         |
| ~ sem asterisco | Relativo ao base_date       |
| \*              | Relativo ao evento anterior |
| \*\*            | Relativo a data corrente    |

Exemplos:
Considerando base*date como `2020-01-01 00:00:00`
| Comando | Desc |
|-------------------------------|----------------------------|
|D-1 ** | Ontem |
|D+1 ** | Amanhã |
|D-0 / D+0 | Mesmo valor de base_date |
| H+1 * | Uma hora de diferença em relação ao evento anterior |
| W+1 \_ | Uma semana de diferença em relação ao evento anterior |

## CLI

python -m main

| Argument                   | Obrigatoriedade | Desc                                                                                                                           |
| -------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `--suite` / `-s`           | Obrigatório     | Especifica um nome de suite ou uma lista de suites. Exemplo: `--suite suite1 suite2`                                           |
| `--testcase` / `-t`        | Opcional        | Especifica um ID de teste criado em test.yaml. Exemplo: `--testcase ACT_001 ACT_002`                                           |
| `--datasetid` / `-ds`      | Opcional        | Personaliza nome de dataset do BigQuery para a execução. Exemplo: `--datasetid ds_my_test`. Por default assume em config.yaml. |
| `--run` / `-r`             | Opcional        | Gera um teste simulado sem executar resultados, apenas o envio do mock de dados. Exemplo: `--run False`. Por default é `True`. |
| `--schema` / `-sch`        | Opcional        | Atualiza schema de tabelas localmente.                                                                    |
| `--persist-dataset` / `-p` | Opcional        | Mantém o resultado do dataset após a execução do teste no ambiente BigQuery.                                                   |
