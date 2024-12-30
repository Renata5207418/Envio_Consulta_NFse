from flask import Flask, request, render_template, jsonify, send_file
import os
import pandas as pd
from io import BytesIO
from directory import read_data_from_excel, SoapRequestGenerator, send_soap_request, dados, lista
from utils import verify_submission
import unicodedata
import html
import re

app = Flask(__name__)
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = {'xlsx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

processed_status = []
uploaded_filename = None


def allowed_file(filename):
    """
      Verifica se o arquivo enviado possui uma extensão permitida.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def normalizar_coluna(nome_coluna):
    """
      Normaliza o nome de uma coluna removendo acentos e convertendo para minúsculas.
    """
    nome_coluna = unicodedata.normalize('NFKD', nome_coluna).encode('ASCII', 'ignore').decode('ASCII')
    return nome_coluna.lower()


def normalizar_texto(texto):
    """
       Normaliza o texto removendo acentos, espaços extras e convertendo para minúsculas.
    """
    if pd.isna(texto):
        return texto
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.lower().strip()
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def normalize_column_names(columns):
    """
     Normaliza os nomes das colunas, removendo sufixos e convertendo para minúsculas.
    """
    normalized_columns = []
    for col in columns:
        normalized_col = col.split('_')[0].lower().strip()
        normalized_columns.append(normalized_col)
    return normalized_columns


def preencher_municipio(planilha_caminho, banco_territorial_caminho):
    """
       Preenche os códigos municipais nas planilhas baseados em um banco territorial de referência.

       Parâmetros:
           planilha_caminho (str): Caminho da planilha enviada pelo usuário.
           banco_territorial_caminho (str): Caminho do banco de dados territorial.

       Exceções:
           ValueError: Erro em formato de colunas ou dados ausentes.
    """
    print(f"Processando a planilha: {planilha_caminho}")
    print(f"Usando o banco territorial: {banco_territorial_caminho}")

    # Mapeamento de códigos para estados (UF)
    uf_mapping = {
        11: 'RO', 12: 'AC', 13: 'AM', 14: 'RR', 15: 'PA', 16: 'AP', 17: 'TO',
        21: 'MA', 22: 'PI', 23: 'CE', 24: 'RN', 25: 'PB', 26: 'PE', 27: 'AL', 28: 'SE', 29: 'BA',
        31: 'MG', 32: 'ES', 33: 'RJ', 35: 'SP',
        41: 'PR', 42: 'SC', 43: 'RS',
        50: 'MS', 51: 'MT', 52: 'GO', 53: 'DF'
    }

    xls = pd.ExcelFile(planilha_caminho)
    df_banco_territorial = pd.read_excel(banco_territorial_caminho)

    print("Colunas na planilha do banco territorial:", df_banco_territorial.columns)

    df_banco_territorial['UF'] = df_banco_territorial['UF'].map(uf_mapping)

    df_banco_territorial['Cidade'] = df_banco_territorial['Cidade'].apply(normalizar_texto)
    df_banco_territorial['chave'] = ((df_banco_territorial['Cidade'] + '/' + df_banco_territorial['UF'].str.upper())
                                     .apply(normalizar_texto))

    print("Chaves no banco territorial:", df_banco_territorial['chave'].unique())

    df_dict = {}

    for sheet_name in xls.sheet_names:
        df_planilha = pd.read_excel(planilha_caminho, sheet_name=sheet_name)
        print(f"Processando aba: {sheet_name}")
        print("Colunas na planilha do usuário:", df_planilha.columns)

        df_planilha.columns = normalize_column_names(df_planilha.columns)
        print("Colunas normalizadas:", df_planilha.columns)

        # Validação da coluna cidade/uf
        if 'cidade/uf' not in df_planilha.columns:
            raise ValueError(f"A coluna 'cidade/uf' não está presente na planilha de entrada na aba {sheet_name}.")

        split_columns = df_planilha['cidade/uf'].str.split('/', expand=True)
        if split_columns.shape[1] != 2:
            raise ValueError(f"Erro ao dividir a coluna 'cidade/uf' na aba {sheet_name}. Verifique o formato.")

        # Divide a coluna cidade/uf
        df_planilha[['cidade', 'uf']] = split_columns
        df_planilha['cidade'] = df_planilha['cidade'].apply(normalizar_texto)
        df_planilha['uf'] = df_planilha['uf'].str.upper()

        df_planilha['chave'] = (df_planilha['cidade'] + '/' + df_planilha['uf']).apply(normalizar_texto)

        print("Primeiras linhas da planilha após criar a chave:", df_planilha.head())

        municipio_mapping = dict(zip(df_banco_territorial['chave'], df_banco_territorial['Código Município']))
        df_planilha['municipio'] = df_planilha['chave'].map(municipio_mapping)

        if df_planilha['municipio'].isnull().any():
            linhas_nao_correspondidas = df_planilha[df_planilha['municipio'].isnull()]
            print("Linhas não correspondidas:", linhas_nao_correspondidas)
            raise ValueError(f"Alguns cód de municípios não foram encontrados no banco de dados na aba {sheet_name}.")

        df_planilha = df_planilha.drop(columns=['cidade/uf', 'cidade', 'chave'])

        # Salva o resultado processado
        df_dict[sheet_name] = df_planilha

    # Reescreve a planilha com os dados atualizados
    with pd.ExcelWriter(planilha_caminho, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print("Planilha atualizada com códigos de município e abas preservadas.")


@app.route('/')
def index():
    """Rota para carregar a página inicial."""

    return render_template('index.html')


@app.route('/status')
def status_page():
    return render_template('status.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Rota para fazer upload e processar o arquivo Excel enviado pelo usuário."""

    global processed_status, uploaded_filename
    processed_status = []

    if 'file' not in request.files:
        return 'Nenhum arquivo encontrado', 400

    file = request.files['file']
    if file.filename == '':
        return 'Nenhum arquivo selecionado', 400

    if file and allowed_file(file.filename):
        uploaded_filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_filename)
        file.save(file_path)

        BANCO_TERRITORIAL_CAMINHO = os.getenv('BANCO_TERRITORIAL', 'referencia/relatorio_municipio.xls')
        preencher_municipio(file_path, BANCO_TERRITORIAL_CAMINHO)

        status_list = process_file(file_path)
        processed_status.extend(status_list)
        return jsonify(status_list)
    else:
        return 'Arquivo não permitido', 400


def process_file(file_path):
    dfs = read_data_from_excel(file_path)
    status_list = []

    for sheet_name, df in dfs.items():
        if sheet_name in dados:
            cnpj_prestador, inscricao_municipal_prestador = dados[sheet_name]
        else:
            continue

        soap_request_gen = SoapRequestGenerator()

        rps_inicial = int(df.iloc[0]['rps']) if 'rps' in df.columns else 1
        rps_counter = rps_inicial

        for index, row in df.iterrows():
            if sheet_name == "simply":
                aliquota = 0.0253
            elif sheet_name == "dm":
                aliquota = 0.0414
            else:
                aliquota = 0.05

            kwargs = {
                'cnpj': cnpj_prestador,
                'inscricao_municipal': inscricao_municipal_prestador,
                'valor_rps': rps_counter,
                'prestador_cnpj': cnpj_prestador,
                'prestador_inscricao': inscricao_municipal_prestador,
                'tomador_cnpj': row.get('cnpj', ''),
                'tomador_razao_social': html.escape(row.get('razao', '')),
                'tomador_endereco': row.get('logradouro', ''),
                'tomador_numero': row.get('numero', ''),
                'tomador_bairro': row.get('bairro', ''),
                'tomador_codigo_municipio': row.get('municipio', ''),
                'tomador_uf': row.get('uf', ''),
                'tomador_cep': row.get('cep', ''),
                'valor_liquido_nfse': row.get('valor', ''),
                'item_lista_servico': lista.get(sheet_name, ['0'])[0],
                'aliquota': aliquota,
                'codigo_cnae': '8219999' if sheet_name == 'consultoria' else '0',
                'descricao': row.get('descricao', '')
            }

            soap_request = soap_request_gen.create_soap_request(**kwargs)
            rps_counter += 1

            numero_lote = soap_request_gen.numero_lote_dinamico(valor_rps=kwargs['valor_rps'])

            soap_request_lote = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <RecepcionarLoteRps xmlns="https://www.e-governeapps2.com.br/">
      <EnviarLoteRpsEnvio>
        <LoteRps>
          <NumeroLote>{numero_lote}</NumeroLote>
          <Cnpj>{cnpj_prestador}</Cnpj>
          <InscricaoMunicipal>{inscricao_municipal_prestador}</InscricaoMunicipal>
          <QuantidadeRps>1</QuantidadeRps>
          <ListaRps>
            <Rps>
              <InfRps>
                {soap_request.split('<InfRps>')[1].split('</InfRps>')[0]}
              </InfRps>
            </Rps>
          </ListaRps>
        </LoteRps>
      </EnviarLoteRpsEnvio>
    </RecepcionarLoteRps>
  </soap:Body>
</soap:Envelope>"""

            response = send_soap_request(soap_request_lote)
            status_text = "Sucesso" if "Protocolo" in response.text else "Erro"

            if status_text == "Sucesso":
                protocolo_numero = response.text.split("<Protocolo>")[1].split("</Protocolo>")[0]
                status_verificacao = verify_submission(cnpj_prestador, inscricao_municipal_prestador, protocolo_numero)
            else:
                protocolo_numero = "N/A"
                status_verificacao = "Erro ao processar a NFS-e: " + response.text

            status = [
                kwargs['valor_rps'],
                kwargs['tomador_cnpj'],
                kwargs['tomador_razao_social'],
                kwargs['tomador_endereco'],
                kwargs['tomador_numero'],
                kwargs['tomador_codigo_municipio'],
                kwargs['tomador_uf'],
                kwargs['tomador_cep'],
                kwargs['tomador_bairro'],
                kwargs['valor_liquido_nfse'],
                kwargs['descricao'],
                protocolo_numero,
                status_verificacao
            ]
            status_list.append(status)

    return status_list


@app.route('/export', methods=['GET'])
def export_status():
    global processed_status, uploaded_filename
    if uploaded_filename is None:
        return 'Nenhum arquivo processado disponível para exportação', 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_filename)

    xls = pd.ExcelFile(file_path)

    df_dict = {}
    processed_status_index = 0

    for sheet_name in xls.sheet_names:
        df_planilha = pd.read_excel(file_path, sheet_name=sheet_name)

        df_planilha['Protocolo'] = None
        df_planilha['Status Verificação'] = None

        for i in range(len(df_planilha)):
            if processed_status_index < len(processed_status):
                df_planilha.at[i, 'Protocolo'] = processed_status[processed_status_index][11]
                df_planilha.at[i, 'Status Verificação'] = processed_status[processed_status_index][12]
                processed_status_index += 1

        df_planilha = df_planilha.reindex(columns=[
            'vazio', 'rps', 'vazio.1', 'cnpj', 'razao', 'logradouro',
            'numero', 'cep', 'bairro', 'valor', 'descricao', 'obs',
            'uf', 'municipio', 'Protocolo', 'Status Verificação'
        ])

        df_dict[sheet_name] = df_planilha

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    output.seek(0)

    return send_file(output, as_attachment=True, download_name=f"{uploaded_filename[:-5]}_processada.xlsx",
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route('/status_data', methods=['GET'])
def status_data():
    global processed_status
    return jsonify(processed_status)


if __name__ == '__main__':
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    app.run(debug=DEBUG_MODE)
