from tests.resource.utils import generator as gen
from tests.resource.utils.components import Interval
from tests.resource.utils.components import Practitioner

class Mock:

    """
        Classe para geração da Fato Produção Exame em formato Mock

        Attributes:
        :param tree: Dicionário de configurações informadas no YAML.
        :param person: Instância de uma classe de components.
        :param event: Lista de eventos para herança.
    """

    tree = None

    def __init__(self, tree:dict, person, event=dict()):
        Mock.tree = tree

        self.my_string = self.cip(person)
        self.my_datetime = self.my_datetime()
        self.my_integer = self.my_integer()


    def my_string(self) -> str:

        return Mock.tree.get('my_string')

    def my_datetime(self) -> str:

        return Mock.tree.get('interval2')

    def my_integer(self) -> int:

        return Mock.tree.get('my_integer')
