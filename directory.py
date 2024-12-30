import os
import pandas as pd
import datetime
import requests
import html
from dotenv import load_dotenv  # Para carregar variáveis de ambiente

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()
"""
Módulo: processamento_soap.py
Descrição: Processamento de dados para envio de solicitações SOAP, utilizando informações
extraídas de planilhas Excel para geração automática de RPS (Recibo Provisório de Serviços).

Funcionalidades:
- Leitura e processamento de planilhas Excel.
- Geração dinâmica de requisições SOAP para comunicação com serviços web.
- Organização e exportação dos arquivos XML gerados para envio.

Dependências:
- Pandas
- Requests
- Variáveis de Ambiente (dotenv)
"""

SOAP_URL = 'https://isscuritiba.curitiba.pr.gov.br/Iss.NfseWebService/nfsews.asmx'

dados = {
    "categoria_1": [os.getenv('CNPJ_CATEGORIA_1'), os.getenv('IM_CATEGORIA_1')],
    "categoria_2": [os.getenv('CNPJ_CATEGORIA_2'), os.getenv('IM_CATEGORIA_2')],
    "categoria_3": [os.getenv('CNPJ_CATEGORIA_3'), os.getenv('IM_CATEGORIA_3')],
    "categoria_4": [os.getenv('CNPJ_CATEGORIA_4'), os.getenv('IM_CATEGORIA_4')]
}

lista = {
    "categoria_1": ["0000"],
    "categoria_2": ["0000"],
    "categoria_3": ["0000"],
    "categoria_4": ["0000"]
}


class SoapRequestGenerator:
    """
    Classe responsável por gerar solicitações SOAP para envio de RPS.

    Métodos:
    - numero_lote_dinamico: Gera um número de lote dinâmico baseado na data e número RPS.
    - create_soap_request: Cria o corpo XML da solicitação SOAP.
    """
    def __init__(self, initial_rps_number=1):
        """
        Inicializa o gerador de requisições SOAP.

        Parâmetros:
            initial_rps_number (int): Número inicial do RPS (default: 1).
        """
        self.rps_counter = initial_rps_number

    def numero_lote_dinamico(self, valor_rps):
        """
        Gera um número de lote dinâmico com base na data atual e número RPS.

        Parâmetros:
            valor_rps (int): Número do RPS atual.

        Retorna:
            int: Número do lote gerado dinamicamente.
        """
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d")
        numero_lote_str = f"{timestamp}{valor_rps}"
        numero_lote = int(numero_lote_str)
        return numero_lote

    def create_soap_request(self, valor_liquido_nfse, descricao, valor_rps, item_lista_servico, aliquota, codigo_cnae,
                            **kwargs):
        """
        Cria o corpo XML de uma requisição SOAP para envio de RPS.

        Parâmetros:
            valor_liquido_nfse (float): Valor líquido da nota fiscal.
            descricao (str): Descrição do serviço.
            valor_rps (int): Número do RPS.
            item_lista_servico (str): Código do serviço.
            aliquota (float): Alíquota aplicada.
            codigo_cnae (int): Código CNAE do serviço.
            kwargs (dict): Outros parâmetros opcionais para preencher os campos SOAP.

        Retorna:
            str: Corpo XML formatado para envio SOAP.
        """
        data_emissao = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        numero_lote = self.numero_lote_dinamico(valor_rps)
        self.rps_counter += 1

        tomador_razao_social = html.escape(kwargs.get('tomador_razao_social', ''))

        tomador_cpf_cnpj = kwargs.get('tomador_cnpj', '').replace('.', '').replace('-', '').replace('/', '')
        if len(tomador_cpf_cnpj) == 11:
            cpf_cnpj_tag = f"<Cpf>{tomador_cpf_cnpj}</Cpf>"
        else:
            cpf_cnpj_tag = f"<Cnpj>{tomador_cpf_cnpj}</Cnpj>"

        return f"""<?xml version="1.0" encoding="utf-8"?> <soap:Envelope 
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"> <soap:Body> <RecepcionarLoteRps 
        xmlns="https://www.e-governeapps2.com.br/"> <EnviarLoteRpsEnvio> <LoteRps> <NumeroLote>
{numero_lote}</NumeroLote>
          <Cnpj>{kwargs.get('cnpj', '')}</Cnpj>
          <InscricaoMunicipal>{kwargs.get('inscricao_municipal', '')}</InscricaoMunicipal>
          <QuantidadeRps>{int(self.rps_counter - 1)}</QuantidadeRps>
          <ListaRps>
            <Rps>
              <InfRps>
                <IdentificacaoRps>
                  <Numero>{valor_rps}</Numero>
                  <Serie>1</Serie>
                  <Tipo>1</Tipo>
                </IdentificacaoRps>
                <DataEmissao>{data_emissao}</DataEmissao>
                <NaturezaOperacao>1</NaturezaOperacao>
                <OptanteSimplesNacional>1</OptanteSimplesNacional>
                <IncentivadorCultural>2</IncentivadorCultural>
                <Status>1</Status>
                <Servico>
                  <Valores>
                    <ValorServicos>{valor_liquido_nfse}</ValorServicos>
                    <ValorDeducoes>0</ValorDeducoes>
                    <ValorPis>0</ValorPis>
                    <ValorCofins>0</ValorCofins>
                    <ValorInss>0</ValorInss>
                    <ValorIr>0</ValorIr>
                    <ValorCsll>0</ValorCsll>
                    <IssRetido>2</IssRetido>
                    <ValorIss>0</ValorIss>
                    <ValorIssRetido>0</ValorIssRetido>
                    <OutrasRetencoes>0</OutrasRetencoes>
                    <BaseCalculo>{kwargs.get('base_calculo', valor_liquido_nfse)}</BaseCalculo>
                    <Aliquota>{aliquota}</Aliquota>
                    <ValorLiquidoNfse>{valor_liquido_nfse}</ValorLiquidoNfse>
                    <DescontoIncondicionado>0</DescontoIncondicionado>
                    <DescontoCondicionado>0</DescontoCondicionado>
                  </Valores>
                  <ItemListaServico>{item_lista_servico}</ItemListaServico>
                  <CodigoCnae>{codigo_cnae}</CodigoCnae>
                  <CodigoTributacaoMunicipio>{kwargs.get('CodigoTributacaoMunicipio')}</CodigoTributacaoMunicipio>
                  <Discriminacao>{descricao}</Discriminacao>
                  <CodigoMunicipio>4106902</CodigoMunicipio>
                </Servico>
                <Prestador>
                  <Cnpj>{kwargs.get('prestador_cnpj', '')}</Cnpj>
                  <InscricaoMunicipal>{kwargs.get('prestador_inscricao', '')}</InscricaoMunicipal>
                </Prestador>
                <Tomador>
                  <IdentificacaoTomador>
                    <CpfCnpj>
                      {cpf_cnpj_tag}
                    </CpfCnpj>
                  </IdentificacaoTomador>
                  <RazaoSocial>{tomador_razao_social}</RazaoSocial>
                  <Endereco>
                    <Endereco>{kwargs.get('tomador_endereco', '')}</Endereco>
                    <Numero>{kwargs.get('tomador_numero', '')}</Numero>
                    <Bairro>{kwargs.get('tomador_bairro', '')}</Bairro>
                    <CodigoMunicipio>{kwargs.get('tomador_codigo_municipio', '')}</CodigoMunicipio>
                    <Uf>{kwargs.get('tomador_uf', '')}</Uf>
                    <Cep>{kwargs.get('tomador_cep', '')}</Cep>
                  </Endereco>
                  <Contato>
                    <Email>financeiro@scryta.com.br</Email>
                  </Contato>
                </Tomador>
              </InfRps>
            </Rps>
          </ListaRps>
        </LoteRps>
      </EnviarLoteRpsEnvio>
    </RecepcionarLoteRps>
  </soap:Body>
</soap:Envelope>"""


def read_data_from_excel(file_path):
    """
    Lê dados de um arquivo Excel e retorna um dicionário com as abas.

    Parâmetros:
        file_path (str): Caminho do arquivo Excel.

    Retorna:
        dict: Dicionário com DataFrames por aba.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    dfs = pd.read_excel(file_path, sheet_name=None)
    return dfs


def send_soap_request(soap_request):
    """
    Envia uma requisição SOAP para o servidor especificado.

    Parâmetros:
        soap_request (str): Corpo da requisição SOAP em XML.

    Retorna:
        requests.Response: Resposta do servidor.
    """
    headers = {
        'Content-Type': 'text/xml; charset=utf-8',
        'SOAPAction': 'https://www.e-governeapps2.com.br/RecepcionarLoteRps'
    }
    response = requests.post(SOAP_URL, data=soap_request, headers=headers)
    return response


def main(excel_file_path, output_dir):
    dfs = read_data_from_excel(excel_file_path)

    for sheet_name, df in dfs.items():
        print(f"Processando aba: {sheet_name}")
        print(f"Abas encontradas: {list(dfs.keys())}")

        for sheet_name, df in dfs.items():
            print(f"Processando aba: {sheet_name}")
            print(f"Abas encontradas: {list(dfs.keys())}")

            if sheet_name in dados:
                cnpj_prestador, inscricao_municipal_prestador = dados[sheet_name]
                item_lista_servico = lista[sheet_name][0]

                if sheet_name == "simply":
                    aliquota = 0.0253
                elif sheet_name == "dm":
                    aliquota = 0.0414
                else:
                    aliquota = 0.05

                codigo_cnae = 8219999 if sheet_name == "consultoria" else 0
            else:
                print(f"Nome da aba '{sheet_name}' não encontrado no dicionário de dados.")
                continue

        print(f"Colunas disponíveis na aba '{sheet_name}': {list(df.columns)}")

        soap_request_gen = SoapRequestGenerator()
        rpss = []

        for index, row in df.iterrows():
            valor_rps = row.get('rps', '')
            kwargs = {
                'cnpj': cnpj_prestador,
                'inscricao_municipal': inscricao_municipal_prestador,
                'valor_rps': valor_rps,
                'prestador_cnpj': cnpj_prestador,
                'prestador_inscricao': inscricao_municipal_prestador,
                'tomador_cnpj': row.get('cnpj', ''),
                'tomador_razao_social': row.get('razao', ''),
                'tomador_endereco': row.get('logradouro', ''),
                'tomador_numero': row.get('numero', ''),
                'tomador_bairro': row.get('bairro', ''),
                'tomador_codigo_municipio': row.get('municipio', ''),
                'tomador_uf': row.get('uf', ''),
                'tomador_cep': row.get('cep', ''),
                'valor_liquido_nfse': row.get('valor', ''),
                'descricao': row.get('descricao', ''),
            }

            soap_request = soap_request_gen.create_soap_request(
                valor_liquido_nfse=row.get('valor', ''),
                descricao=row.get('descricao', ''),
                valor_rps=valor_rps,
                item_lista_servico=item_lista_servico,
                aliquota=aliquota,
                codigo_cnae=codigo_cnae,
                **kwargs
            )
            rpss.append(soap_request)

        if rpss:
            soap_request_lote = f"""<?xml version="1.0" encoding="utf-8"?> <soap:Envelope 
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
            xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"> <soap:Body> <RecepcionarLoteRps 
            xmlns="https://www.e-governeapps2.com.br/"> <EnviarLoteRpsEnvio> <LoteRps> <NumeroLote>
{soap_request_gen.numero_lote_dinamico(valor_rps)}</NumeroLote>
          <Cnpj>{cnpj_prestador}</Cnpj>
          <InscricaoMunicipal>{inscricao_municipal_prestador}</InscricaoMunicipal>
          <QuantidadeRps>{len(rpss)}</QuantidadeRps>
          <ListaRps>"""

            for rps in rpss:
                soap_request_lote += f"""
            <Rps>
              <InfRps>
                {rps.split('<InfRps>')[1].split('</InfRps>')[0]}
              </InfRps>
            </Rps>"""

            soap_request_lote += f"""
          </ListaRps>
        </LoteRps>
      </EnviarLoteRpsEnvio>
    </RecepcionarLoteRps>
  </soap:Body>
</soap:Envelope>"""

            output_file_path = os.path.join(output_dir, f"{sheet_name}_lote_request.xml")
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(soap_request_lote)

            response = send_soap_request(soap_request_lote)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")


if __name__ == "__main__":
    """
    Esta seção era utilizada quando o sistema não possuía um frontend.
    Nesse formato, o código acessava diretamente os arquivos nos caminhos especificados no arquivo .env,
    permitindo o processamento manual de um arquivo Excel e a geração dos resultados na pasta de saída.

    Com a implementação de um frontend, o envio dos arquivos e a seleção dos caminhos passaram a ser feitos
    por meio da interface web, tornando essa abordagem opcional para execução direta.
    """
    # Carrega os caminhos do arquivo .env
    excel_file_path = os.getenv('BASE_EXCEL_PATH')
    output_dir = os.getenv('OUTPUT_DIR')
    # Chama a função principal
    main(excel_file_path, output_dir)
