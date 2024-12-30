import requests
import xml.etree.ElementTree as ET

"""
Módulo: utils.py
Descrição: Utilitários para verificação do status de envio de RPS (Recibo Provisório de Serviços) 
por meio de requisições SOAP.

Funcionalidades:
- Geração de requisições SOAP para verificação do status de protocolos enviados.
- Envio de requisições ao web service.
- Análise das respostas retornadas para determinar o status.

Dependências:
- requests
- xml.etree.ElementTree (ET)
"""

SOAP_URL = "https://isscuritiba.curitiba.pr.gov.br/Iss.NfseWebService/nfsews.asmx"
SOAP_ACTION = "https://www.e-governeapps2.com.br/ConsultarLoteRps"


def create_verification_request(cnpj, inscricao_municipal, protocolo):
    """
    Cria o corpo XML para uma requisição SOAP de verificação de envio.

    Parâmetros:
        cnpj (str): CNPJ do prestador de serviço.
        inscricao_municipal (str): Inscrição municipal do prestador.
        protocolo (str): Número do protocolo retornado no envio.

    Retorna:
        str: Corpo XML formatado da requisição SOAP.

    Exemplo:
        >>> create_verification_request("12345678000195", "12345", "987654321")
    """
    soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <ConsultarLoteRps xmlns="https://www.e-governeapps2.com.br/">
      <ConsultarLoteRpsEnvio>
        <Prestador>
          <Cnpj>{cnpj}</Cnpj>
          <InscricaoMunicipal>{inscricao_municipal}</InscricaoMunicipal>
        </Prestador>
        <Protocolo>{protocolo}</Protocolo>
      </ConsultarLoteRpsEnvio>
    </ConsultarLoteRps>
  </soap:Body>
</soap:Envelope>"""
    return soap_request


def send_verification_request(soap_request):
    """
    Envia a requisição SOAP ao web service para verificação do status do protocolo.

    Parâmetros:
        soap_request (str): Corpo XML formatado da requisição SOAP.

    Retorna:
        str: Resposta do web service em formato XML.

    Exemplo:
        >>> response = send_verification_request(soap_request)
        >>> print(response)
    """
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": SOAP_ACTION,
    }
    response = requests.post(SOAP_URL, data=soap_request, headers=headers)
    return response.text


def parse_verification_response(response_text):
    """
    Analisa a resposta SOAP retornada pelo web service e determina o status do protocolo.

    Parâmetros:
        response_text (str): Resposta XML recebida do web service.

    Retorna:
        str: Status do protocolo (Sucesso, Erro ou Status não encontrado).

    Exemplo:
        >>> status = parse_verification_response(response_text)
        'Sucesso: NFS-e encontradas'
    """
    try:
        root = ET.fromstring(response_text)
        lista_nfse = root.findall('.//{https://www.e-governeapps2.com.br/}ListaNfse')
        if lista_nfse:
            status_lote = "Sucesso: NFS-e encontradas"
        else:
            lista_mensagem = root.findall('.//{https://www.e-governeapps2.com.br/}ListaMensagemRetorno')
            if lista_mensagem:
                status_lote = "Erro: Mensagens de retorno encontradas"
            else:
                status_lote = "Status não encontrado"
        return status_lote
    except ET.ParseError:
        return "Erro ao analisar a resposta"


def verify_submission(cnpj, inscricao_municipal, protocolo):
    """
    Verifica o status de um protocolo enviado utilizando requisições SOAP.

    Parâmetros:
        cnpj (str): CNPJ do prestador.
        inscricao_municipal (str): Inscrição municipal do prestador.
        protocolo (str): Número do protocolo gerado no envio.

    Retorna:
        str: Status do protocolo após análise da resposta.

    Exemplo:
        >>> verify_submission("12345678000195", "12345", "987654321")
        'Sucesso: NFS-e encontradas'
    """
    soap_request = create_verification_request(cnpj, inscricao_municipal, protocolo)
    response_text = send_verification_request(soap_request)
    status = parse_verification_response(response_text)
    return status
