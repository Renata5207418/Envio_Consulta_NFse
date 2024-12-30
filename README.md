# 📄 Sistema de Processamento e Envio de NFS-e

Este projeto automatiza o **envio e consulta de NFS-e** (Notas Fiscais de Serviços Eletrônicas) através de um serviço web SOAP. Ele permite o processamento de arquivos Excel, geração dinâmica de requisições SOAP e verificação do status de protocolos.

---

## 🚀 **Funcionalidades**
- 📥 **Upload de Arquivos Excel**: Processa planilhas e extrai dados.  
- 📨 **Geração de Requisições SOAP**: Envia lotes de RPS para o web service configurado.  
- 🔍 **Consulta de Status**: Verifica o status de protocolos enviados.  
- 📊 **Exportação de Resultados**: Gera arquivos de saída processados.  
- 🌐 **Integração com Frontend**: Interface web para facilitar o envio de arquivos.

---

## 🛠️ **Pré-requisitos**

- **Python 3.10 ou superior**  
- Gerenciador de pacotes `pip` instalado.  
- Ambiente virtual configurado (`venv` ou similar).  

---

## 🧩 **Instalação**

1. Clone o repositório:
   ```bash
   git clone https://github.com/usuario/nfse-soap-project.git
   cd nfse-soap-project
   ```

2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Linux/Mac
   .venv\Scripts\activate        # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```


## ⚙️ **Execução do Sistema**

1. **Executar o Servidor Flask**:
   ```bash
   python app.py
   ```

2. **Upload do Arquivo**:
   - Acesse a interface web.
   - Faça o upload do arquivo Excel no formato correto.  

3. **Verificar Status**:
   - Utilize o painel para consultar o status de envio dos protocolos.

---

## 📊 **Logs**

Logs de execução e diagnóstico são gerados automaticamente na pasta **logs/** ou no arquivo **`soap_debug.log`**. Certifique-se de revisar possíveis erros lá.

---

## 🧑‍💻 **Tecnologias Utilizadas**

- **Backend:** Flask  
- **Manipulação de Dados:** Pandas  
- **Requisições HTTP:** Requests  
- **Geração e Análise de XML:** xml.etree.ElementTree  
- **Ambiente Seguro:** Python-dotenv  

---

## ❓ **Dúvidas ou Problemas?**

Se encontrar algum problema ou tiver dúvidas sobre o uso, abra uma **issue** neste repositório.

---