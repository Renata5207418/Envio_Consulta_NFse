import os
import pandas as pd

"""
Módulo: file_handler.py
Descrição: Este módulo contém funções utilitárias para manipulação de arquivos,
como salvar uploads e ler arquivos Excel (.xlsx).

Funcionalidades:
- Salvar arquivos enviados via upload em um diretório especificado.
- Ler arquivos Excel e retornar os dados em formato de DataFrame do Pandas.

Dependências:
- os
- pandas
"""


def save_uploaded_file(file, upload_folder, filename):
    """
    Salva um arquivo enviado pelo usuário no diretório especificado.

    Parâmetros:
        file (werkzeug.datastructures.FileStorage): Arquivo enviado pelo usuário via upload.
        upload_folder (str): Caminho do diretório onde o arquivo será salvo.
        filename (str): Nome do arquivo a ser salvo.

    Retorna:
        str: Caminho completo do arquivo salvo.

    Exemplo:
        >>> save_uploaded_file(file, 'uploads', 'documento.xlsx')
        'uploads/documento.xlsx'
    """
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path


def read_xlsx(file_path):
    """
        Lê um arquivo Excel (.xlsx) e retorna os dados em formato de DataFrame.

        Parâmetros:
            file_path (str): Caminho completo do arquivo Excel a ser lido.

        Retorna:
            pandas.DataFrame: Dados lidos do arquivo Excel.

        Exemplo:
            >>> df = read_xlsx('uploads/documento.xlsx')
            >>> print(df.head())
               Nome      Idade
            0   João       25
            1   Maria      30
        """
    return pd.read_excel(file_path)
