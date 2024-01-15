"""
    Script responsável por realizar a construção do Data Mock, lendo
    e validando a estrutura do YAML e enviando os dados lidos para
    camadas de entitities e componentes para a criação do mock.
"""

from __future__ import annotations
import pandas as pd
from copy import deepcopy
from tests.resource.entities import mockups
from tests.resource.utils import components
from tests.resource.utils.logger import logger
from tests.resource.utils import validator as val


class Mocker:
    """
        Classe responsável pela construção de Data Mocks.
    """

    def __init__(self, path: str, suite: str, testcase: str):

        self.suite = suite
        self.testcase = testcase
        self.yaml = self._yaml(path)
        self.trees = dict()
        self.last_date = None
        self.last_inherance = 0
        self.settings = self._settings()
        self.person = self._person()
        self.key = self._key()
        self.documentation = self._documentation()
        self.unittests = self._unittests()
        self.titles = self._titles()
        self.identifiers = self._identifiers()
        self.events = self._events()

    def _yaml(self, path: str) -> dict:
        """
            Carrega o arquivo de YAML e filtra apenas os valores
            correspondentes ao testcase e configuração de presets.
        """

        location = path.replace('test.py', 'test.yaml')
        target = val.read_file(dir=location)

        return target[self.testcase] 

    def _mockups(self, target:str) -> str:
        """
            Determina qual instância de mockup deve ser utilizada
            a partir do nome de uma tabela.

            target -> Referência de identificação do MockUp
        """

        to_find = set(target.split('_'))

        def similarity(set1: set, set2: set) -> int:
            """
                Fórmula de Índice de Jaccard para determinar melhor escolha.

                set1 -> Conjunto de Busca
                set2 -> Conjunto de Comparação
            """

            intersection = len(set1.intersection(set2))
            union = len(set1) + len(set2) - intersection
            return intersection / union
        
        matches = {key: similarity(to_find, set(key.split('_'))) for key in mockups.keys()}
        best_choice = max(matches, key=matches.get)

        return mockups.get(best_choice)

    def _settings(self) -> dict:
        """
            Carrega do testcase as informações globais de parâmetros.
        """

        if 'settings' not in self.yaml.keys():
            raise Exception('Testcase does not have a settings set.')

        tree = self.yaml['settings']

        if 'base_date' not in tree.keys():
            raise Exception('Base date for test case not found.')

        tree['base_date'] = components.Base_Date(str(tree.get('base_date'))).date
        
        return tree

    def _person(self) -> components.Person:
        """
            Verifica se o testcase possui valores globais obrigatórios
            e opcionais para o Paciente e retorna uma instância de componente.
        """
        # Retorna a instância de um novo paciente
        return components.Person(
            base_date=self.settings.get('base_date'),
            tree=self.yaml.get('person', dict())
        )

    def _documentation(self) -> str:
        """
            Retorna a descrição do cenário de teste
        """

        return self.yaml['documentation']

    def _unittests(self) -> dict:
        """
            Retorna valores pretendidos para testes unitários.
        """

        if 'unittests' not in self.yaml.keys():
            raise Exception('Testcase does not have unittests.')

        return self.yaml['unittests']

    def _tree(self, event) -> dict:
        """
            Atualiza o intervalo de datas entre eventos e recicla
            eventos já instanciados por suas chamadas em títulos.
        """

        # Obtém os parâmetros do evento recebido.
        tree = list(event.values())[0]
        diffs = dict()
        
        # Procura para cada parâmetro do evento, ocorrências de listas
        for key, value in tree.items():

            # Se o valor do parâmetro for uma lista (com exceção à herança)
            if isinstance(value, list) and key != 'parents':

                # Para cada elemento na lista, se o seu nome corresponder a
                # uma instância então é feito a troca.
                for index, element in enumerate(value):
                    if any(_key.startswith(element) for _key in self.trees.keys()):
                        value[index] = next((self.trees[_key] for _key in self.trees if _key.startswith(element)), None)

            # Sobrescreve o valor de um grupo referenciado por outra instância acesso via padrão instance.value
            elif any(_key.startswith(str(value).split('.')[0])  for _key in self.trees.keys()) and key != 'parents' and value != '':

                instancied = next((self.trees[_key] for _key in self.trees if _key.startswith(str(value).split('.')[0])), None)
                tree[key] = instancied.get(str(value).split('.')[-1])

            if isinstance(value, str) and val.is_interval_alias(value) and key != 'parents' and key != 'interval':
                tree[key] = components.Interval(absolute_date=self.settings.get('base_date'), relative_date=self.last_date, diff=value).interval_date
                diffs[value] = tree.get(key)

        if diffs:
            recent = max(diffs, key=diffs.get)
            intern_date = components.Interval(absolute_date=self.settings.get('base_date'), relative_date=self.last_date, diff=str(recent))
            tree['interval2'] = intern_date.interval_date
            tree['interval'] = self.settings.get('base_date'), self.last_date, str(recent)       
            self.last_date = diffs.get(recent)
        else:
            intern_date = components.Interval(absolute_date=self.settings.get('base_date'), relative_date=self.last_date, diff=str(tree.get('interval')))
            tree['interval2'] = intern_date.interval_date
            tree['interval'] = self.settings.get('base_date'), self.last_date, str(tree.get('interval'))
            self.last_date = tree.get('interval2')

        return tree

    def _options(self, alias: str, mirror: dict, forbidden: bool = True) -> dict:
        """
            Função que realiza o replace de valores-_key do 
            mock com as _keys encontradas no agrupamento options
            e devolve o mock com os novos valores sobrescritos.
        """
        custom = dict()

        if 'options' in self.yaml:
            for step in self.yaml['options']:
                if alias == list(step.keys())[0]:
                    custom = list(step.values())[0]

            if forbidden:
                custom.pop('table_name', None)

            for key in custom.keys():
                if key in mirror:
                    mirror[key] = custom.get(key)

        return mirror

    def _titles(self) -> dict:
        """
            Obtém a lista do nome de todos os agrupamentos
            de eventos. Retorna erro casa haja repetição de nomes.
        """
        
        titles = dict()

        # Reconhece todos os títulos de agrupamentos
        for index, event in enumerate(self.yaml['mockup']):
            title = list(event.keys())[0]
            sequential_name = f'row_{index + 1}'
            titles[sequential_name] = title

            if not val.is_table_id(content=title):
                raise Exception(f'Title mockup {title} is not a valid table_id format')

        return titles

    def _identifiers(self) -> list:
        """
            Obtém uma lista única do prefixo de todos os títulos
        """

        unique = list()
        for title in self.titles.values():
            unique.append(title.split('.')[-1])

        return list(set(unique))

    def _events(self) -> dict:
        """
            Propriedade responsável por criar a instância
            de entidades majoritárias conforme o agrupamento
            informado pelo YAML.
        """
        
        # Realiza a iteração para todos os agrupamentos de eventos
        for index, event in enumerate(self.yaml['mockup']):

            mock = None
            inheritance = list()

            # Obtém o nome do título do evento atual
            title = list(event.keys())[0]
            
            # Verifica seu agrupamento substituindo nome de outros agrupamentos
            # por suas respectivas instâncias.
            tree = self._tree(event=deepcopy(event))

            # Determina o identificador adequado para instância
            table_name = title.split('.')[-1]
            mockup = self._mockups(table_name)

            # Verifica se o evento atual deve herdar de outro evento
            # criando uma lista de todas as heranças solicitadas
            if 'parents' in tree.keys():
                for required in tree.get('parents'):
                    found = [valor for _key, valor in self.trees.items() if _key.startswith(required)][0]
                    if found is not None:
                        inheritance.append(found)
                
                # Cria uma nova instância do evento atual para cada herança solicitada
                for index, entitie in enumerate(inheritance) or [None]:
                    if entitie:
                        mock = mockup(tree=tree, person=self.person, event=entitie)
                        setattr(mock, 'interval', tree.get('interval2'))
                        setattr(mock, 'main_name', title)
                        setattr(mock, 'table_name', table_name)
                        mirror = deepcopy(mock).__dict__
                        #self.last_date = tree.get('interval2')
                        self.last_inherance += index + 1
                        #self.trees[f'{title}.__parent__{index + 1}'] = mirror
                        self.trees[f"row_parent_{self.last_inherance}.{table_name}"] = mirror

            
            # Cria a instância de um evento atual sem herança requerida.
            else:
                mock = mockup(tree=tree, person=self.person)
                setattr(mock, 'interval', tree.get('interval2'))
                setattr(mock, 'main_name', title)
                setattr(mock, 'table_name', table_name)
                mirror = deepcopy(mock).__dict__
                #self.last_date = mock.tree.get('interval2')
                self.trees[f"row_{index + 1}.{table_name}"] = mirror

            logger.info(f'Mocked {table_name}')

        # Preenche um dicionário onde todas as entidades únicas são _keys
        group_entities = dict()
        for identifier in self.identifiers:
            group_entities[identifier] = list()
            
        # Une todas as entidades que são do mesmo tipo para o mesmo valor de _key
        for key, value in self.trees.items():
            for entitie_key in group_entities:
                if key.split('.')[-1] == entitie_key:
                    group_entities[entitie_key].append(value)

        # Realiza a concatenação de dataframes para cada lista como valor nas _keys
        for entitie, dataframes in group_entities.items():
            mocked = None
            if dataframes:
                mount = pd.DataFrame(dataframes)
                mocked = mount.convert_dtypes()
            group_entities[entitie] = mocked

        return group_entities

    def _key(self) -> str:
        """
            Retorna o person key da instância gerada para o teste.
        """
        return self.person.key.lower()


def build(path: str, suite: str, testcase: str) -> Mocker:
    """
        Método responsável por fazer o Build do Mock
    """

    try:
        logger.info(f'Starting Data Mock {suite.upper()} {testcase.upper()}')
        return Mocker(path=path, suite=suite, testcase=testcase)
    except Exception as e:
        logger.critical('Cannot create Data Mock!')
        raise e
