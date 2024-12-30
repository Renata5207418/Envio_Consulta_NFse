import re

"""
Módulo: data_validation.py
Descrição: Este módulo fornece funções para validação e normalização de dados, 
como CNPJs e valores monetários, utilizados em transações financeiras ou cadastros.

Funcionalidades:
- Normalizar CNPJs removendo caracteres não numéricos.
- Normalizar valores monetários, substituindo vírgulas por pontos e removendo espaços.
- Validar e retornar os dados normalizados para uso em processamento posterior.
"""


def normalize_cnpj(cnpj):
    """
    Normaliza um CNPJ removendo todos os caracteres não numéricos.

    Parâmetros:
        cnpj (str): O CNPJ a ser normalizado (ex: '12.345.678/0001-95').

    Retorna:
        str: O CNPJ formatado apenas com números (ex: '12345678000195').

    Exemplo:
        >>> normalize_cnpj('12.345.678/0001-95')
        '12345678000195'
    """
    return re.sub(r'\D', '', cnpj)  # Remove qualquer caractere que não seja número


def normalize_valor(valor):
    """
    Normaliza valores monetários para o formato decimal padrão.

    Parâmetros:
        valor (str): O valor a ser normalizado (ex: '1.234,56').

    Retorna:
        str: O valor formatado com ponto como separador decimal (ex: '1234.56').

    Exemplo:
        >>> normalize_valor('1.234,56')
        '1234.56'
    """
    return valor.replace(',', '.').replace(' ', '')  # Substitui vírgulas por pontos e remove espaços


def validate_and_normalize_data(cnpj, valor):
    """
    Valida e normaliza um CNPJ e um valor monetário.

    Parâmetros:
        cnpj (str): O CNPJ a ser validado e normalizado.
        valor (str): O valor monetário a ser validado e normalizado.

    Retorna:
        tuple: Um par de strings contendo o CNPJ e o valor normalizados.

    Exemplo:
        >>> validate_and_normalize_data('12.345.678/0001-95', '1.234,56')
        ('12345678000195', '1234.56')
    """
    # Normaliza os dados usando as funções anteriores
    cnpj_normalizado = normalize_cnpj(cnpj)
    valor_normalizado = normalize_valor(valor)
    return cnpj_normalizado, valor_normalizado

