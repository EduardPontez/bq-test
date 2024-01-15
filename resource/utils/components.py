"""
    Camada de controle para instanciar de forma independente, entidades com atributos
    em comum para facilitar a geração, junção e persistência de dados.
"""


from tests.resource.utils import generator as gen
from tests.resource.utils import validator as val


class Person:
    """
        Classe para montar a instância de uma nova pessoa.

        Attributes:
        :base_date: -> Data de referência para adequar a idade ao período.
    """

    def __init__(self, base_date: str, tree: dict):
        self.cip = self.cip()
        self.cpf = self.cpf(tree)
        self.birth_date = self.birth_date(base_date, tree)
        self.key = self.key()
        self.gender = self.gender(tree)
        self.idcode = self.idcode(tree)
        self.name = self.name()

    def cip(self) -> int:
        """
            Retorna um código CIP de dígitos.
        """
        return gen.idcode(length=10)

    def cpf(self, tree: dict) -> str:
        """
            Persiste um CPF de origem do YAML quando informado.
            Senão, a nova instância subirá com CPF válido aleatório.
        """
        cpf = tree.get('cpf', None)
        return gen.cpf() if not cpf else cpf

    def birth_date(self, base_date: str, tree: dict) -> str:
        """
            Retorna uma data de nascimento formatado em
            YYYY-MM-DD calculado através da idade informada.

            Testa se o valor passado é inteiro e maior que 0.
        """

        age = tree.get('age', gen.idcode(min_value=18, max_value=100))

        assert isinstance(age, int), f'Patient age is not a integer. Got: {age}.'
        assert age > 0, f'Patient age should be greater than zero. Got: {age}.'

        default = gen.birthdate_from_age(age=age, base=base_date)

        return tree.get('birth_date', default)

    def key(self) -> str:
        """
            Retorna o Patient Key codificado através da junção
            do seu CPF com sua data de nascimento em formato SHA1
            de 40 caracteres.
        """
        return gen.hashcode(
            value=f'{self.cpf}{self.birth_date}', 
            mode='SHA1'
        )

    def gender(self, tree: dict) -> str:
        """
            Retorna o gênero do paciente informado.
            Testa se o gênero é M ou F e se é string.
        """

        return tree.get('gender', gen.gender())

    def idcode(self, tree: dict) -> str:
        """
            Persiste um ID de origem do YAML quando informado.
            Senão, retorna um ID para o paciente em texto com 8 dígitos.
        """
        idcode = tree.get('id', None)
        return gen.idcode(numeric=False, length=8) if not idcode else idcode

    def name(self) -> str:
        """
            Retorna um nome completo para o paciente.
            É utilizado em instâncias para Carestream e NLP
        """
        #return gen.propername()
        return ''


class Practitioner:
    """
        Classe para instanciar um novo médico agrupado em NESTED FIELDS.
    """

    def __init__(self):
        self.id_practitioner = self.id_practitioner()
        self.doc_practitioner = self.doc_practitioner()
        self.name_practitioner = self.name_practitioner()
        self.cpf_practitioner = self.cpf_practitioner()

    def id_practitioner(self) -> int:
        """
            Retorna um ID para o médico com 8 dígitos.
        """
        return gen.idcode(length=8)        

    def doc_practitioner(self) -> str:
        """
            Retorna um número de CRM fictício para o médico.
        """
        return gen.crm()

    def name_practitioner(self) -> str:
        """
            Retorna um nome fictício para o médico.
        """
        #return gen.propername()
        return ''

    def cpf_practitioner(self) -> str:
        """
            Persiste um CPF de origem do YAML quando informado.
            Senão, a nova instância subirá com CPF válido aleatório.
        """
        return gen.cpf()


class Interval:
    
    """
        Componente utilizado para calcular diferença entre datas a partir de um 
        intervalo informado. 
    """
    
    def __init__(self, absolute_date: str, relative_date: str = None, diff: str = 'D-0', debit: int = None):

        self.diff = self.diff(diff)
        self.debit = self.debit(debit)
        self.absolute_date = self.absolute_date(absolute_date)
        self.relative_date = self.relative_date(relative_date)
        self.current_date = self.current_date()
        self.chosen_date = self.chosen_date(diff)
        self.interval_date = self.interval_date()

    def diff(self, diff):
        """
            Verifica se a diferença pretendida para calcular nova data é válida.
            O valor pode ser um alias (D-X) ou um número inteiro.
            O valor pode receber um indicador de asterisco *
        """
        target = None

        if diff is None or diff == 'None':
            target = '0'
        else:
            target = str(diff).replace('*', '').replace(' ', '')

        checked = val.is_alias(target)
        
        if checked:
            return checked
        else:
            raise Exception(f'Not a valid interval: {diff}')

    def debit(self, debit):
        return debit

    def absolute_date(self, absolute_date):
        """
            Retorna o base_date absoluto calculado pelo Mocker
        """
        # Se o base date for absoluto (YYYY-MM-DD)
        if val.is_date(absolute_date):
            return val.is_date(absolute_date)

        # Se o base_date for um alias (D-X)
        elif val.is_alias(absolute_date):
            return gen.alias_date(absolute_date, keep_hms=False)

    def relative_date(self, relative_date):
        """
            Determina como data relativa a última data gerada do intervalo anterior.
        """     
        # Verifica se na 1ª passagem é pretendido usar a data relativa que virá
        # como None. Neste caso, a data relativa será do mesmo valor que a absoluta.   
        if relative_date:
            return relative_date
        return self.absolute_date

    def current_date(self):
        return gen.datetime_from_current()
    
    def chosen_date(self, diff):
        """
            Determina se a data base para cálculo do intervalo deve ser feita
            através da data absoluta ou relativa (data anterior).
        """
        indicator = str(diff).count('*')
        if indicator == 1:
            return self.relative_date
        elif indicator == 2:
            return self.current_date
        else:
            return self.absolute_date

    def interval_date(self):
        """
            Calcula a nova data de acordo com a data inicial pretendida e o intervalo.
        """  
        return gen.alias_date(alias=self.diff, keep_hms=False, start_date=self.chosen_date, debit=self.debit)


class Base_Date:
    """
        Classe responsável por determinar o valor da constante de base_date
        informado nos parâmetros do teste. Realiza a conversão da data
        em caso de informação do alias.

        Attributes:
        :param: date -> Data informada podendo assumir YYYY-MM-DD ou um alias 
        Y-X, M-X.
    """
    def __init__(self, date: str):
        self.date = self._date(date)

    def _date(self, date:str) -> str:
        """
            Valida e calcula a data do base_date que será uma constante
        """
        # Se o base date for absoluto (YYYY-MM-DD)
        if val.is_date(date):
            return val.is_date(date)

        # Se o base_date for um alias (D-X)
        elif val.is_alias(date):
            return gen.alias_date(date, keep_hms=False)

        else:
            raise Exception('Not a valid base date.')
