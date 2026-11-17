# Doação Segura — Protótipo 0.1

Este é um protótipo experimental para demonstrar uma primeira triagem de sinais de risco em campanhas de arrecadação.

## O que esta versão faz
- Analisa linguagem de urgência.
- Verifica menções a prestação de contas.
- Compara os nomes informados para beneficiário e recebedor do Pix.
- Faz verificações técnicas muito básicas do link.
- Compara o texto com pequenos exemplos locais de referência.

## Limitações importantes
Esta versão NÃO usa ainda um modelo de IA generativa, não consulta bancos, não confirma a identidade de pessoas, não verifica transações Pix e não determina fraude. O índice é experimental e não representa probabilidade estatística de fraude. É uma demonstração inicial de regras e comparação textual.

## Como executar no computador (opcional)
1. Instale Python 3.10 ou superior.
2. Abra o terminal na pasta do projeto.
3. Execute: `pip install -r requirements.txt`
4. Execute: `streamlit run app.py`
5. O navegador abrirá a plataforma.

## Como publicar gratuitamente no Streamlit Community Cloud
1. Crie uma conta no GitHub.
2. Crie um repositório novo e envie `app.py` e `requirements.txt`.
3. Acesse https://share.streamlit.io/
4. Conecte seu GitHub, escolha o repositório e selecione `app.py`.
5. Clique em Deploy.

## Próximas etapas de desenvolvimento
1. Testar com conjunto de campanhas legítimas e casos documentados.
2. Criar uma base de exemplos rotulados e regras revisáveis.
3. Integrar um modelo de IA por API, com proteção de dados e custos controlados.
4. Melhorar a análise de links e imagens sem armazenar dados sensíveis.
5. Medir falsos positivos e falsos negativos.
