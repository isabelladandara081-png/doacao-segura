import re
import difflib
from urllib.parse import urlparse
import streamlit as st

st.set_page_config(page_title="Doação Segura | Protótipo", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.main {background: #f7f8fc;}
.block-container {padding-top: 2rem; max-width: 1100px;}
.hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#172554,#4338ca); color: white;}
.hero p {color: #e0e7ff; margin-bottom: 0;}
.small-note {color:#64748b; font-size:0.85rem;}
.metric-card {background:white; padding:1rem; border:1px solid #e2e8f0; border-radius:14px;}
</style>
""", unsafe_allow_html=True)

SAMPLE_CAMPAIGNS = [
    {
        "name": "Campanha exemplo A",
        "text": "Ajude Maria no tratamento. Estamos arrecadando para despesas médicas. A prestação de contas será publicada pela associação responsável."
    },
    {
        "name": "Campanha exemplo B",
        "text": "URGENTE! Doe agora, só temos poucas horas. Compartilhe imediatamente. Ajude esta família com qualquer valor."
    },
    {
        "name": "Campanha exemplo C",
        "text": "Estamos arrecadando recursos para compra de alimentos e kits de higiene. A ação será organizada pelo projeto comunitário local."
    },
]

def clean_text(value):
    value = (value or "").lower()
    value = re.sub(r"https?://\S+", " ", value)
    value = re.sub(r"[^a-zà-ú0-9\s]", " ", value)
    return re.sub(r"\s+", " ", value).strip()

def similarity(a, b):
    a, b = clean_text(a), clean_text(b)
    if not a or not b:
        return 0
    return difflib.SequenceMatcher(None, a, b).ratio()

def inspect_url(raw_url):
    if not raw_url.strip():
        return None, []
    candidate = raw_url.strip()
    if "://" not in candidate:
        candidate = "https://" + candidate
    try:
        parsed = urlparse(candidate)
        host = parsed.hostname or ""
    except Exception:
        return None, ["O endereço informado não pôde ser interpretado."]
    findings = []
    if not host or "." not in host:
        findings.append("O endereço parece incompleto ou inválido.")
    if parsed.scheme != "https":
        findings.append("O link não utiliza HTTPS.")
    suspicious_words = ["pix", "doacao", "ajuda", "urgente", "premio", "seguro"]
    if any(word in host.lower() for word in suspicious_words):
        findings.append("O domínio contém termos frequentemente usados em páginas de apelo; isso, isoladamente, não indica fraude.")
    return host, findings

def analyze(text, url, beneficiary, receiver):
    findings = []
    score = 0
    low = (text or "").lower()

    urgency = ["urgente", "agora", "últimas horas", "so hoje", "só hoje",
               "compartilhe imediatamente", "não temos tempo", "prazo acaba"]
    urgency_hits = [term for term in urgency if term in low]
    if urgency_hits:
        score += min(20, 8 + 4 * (len(urgency_hits)-1))
        findings.append(("Atenção", "A campanha usa linguagem de urgência ou pressão para doar."))

    accountability = ["prestação de contas", "nota fiscal", "comprovante",
                      "relatório", "associação", "instituição"]
    if not any(term in low for term in accountability):
        score += 12
        findings.append(("Verificação", "Não foram encontradas referências claras à prestação de contas ou à entidade responsável."))

    if beneficiary.strip() and receiver.strip():
        if clean_text(beneficiary) != clean_text(receiver):
            score += 30
            findings.append(("Atenção importante", "O nome do beneficiário informado é diferente do nome do recebedor do Pix. Confirme a relação entre eles por um canal independente."))
        else:
            findings.append(("Consistência informada", "Os nomes informados para beneficiário e recebedor coincidem. Isso não comprova a legitimidade da campanha."))
    else:
        score += 8
        findings.append(("Informação ausente", "Informe beneficiário e recebedor para permitir essa verificação básica."))

    host, url_findings = inspect_url(url)
    if url_findings:
        score += min(15, 5 * len(url_findings))
        for item in url_findings:
            findings.append(("Link", item))
    elif host:
        findings.append(("Link", f"Domínio identificado: {host}. A análise não confirma a reputação ou propriedade do site."))

    best_match = (0, None)
    for item in SAMPLE_CAMPAIGNS:
        sim = similarity(text, item["text"])
        if sim > best_match[0]:
            best_match = (sim, item["name"])
    if best_match[0] >= 0.72:
        score += 20
        findings.append(("Similaridade", f"O texto é bastante semelhante a um exemplo de referência ({best_match[1]}). Isso é um sinal para revisão, não uma prova de cópia ou fraude."))
    elif best_match[0] >= 0.50:
        score += 8
        findings.append(("Similaridade", "Foi encontrada semelhança parcial com um texto de referência."))

    score = min(score, 100)
    if score >= 50:
        level, color = "Alto", "red"
    elif score >= 25:
        level, color = "Moderado", "orange"
    else:
        level, color = "Baixo", "green"
    return score, level, color, findings, best_match[0]

st.markdown("""
<div class="hero">
  <h1>🛡️ Doação Segura</h1>
  <p>Uma camada de análise para ajudar pessoas a reconhecer sinais de risco antes de doar.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
tab1, tab2, tab3 = st.tabs(["🔎 Analisar campanha", "ℹ️ Como funciona", "🧪 Testar exemplo"])

with tab1:
    st.subheader("Verifique os sinais de uma campanha")
    st.caption("Insira as informações disponíveis. Não envie documentos pessoais, dados bancários completos ou informações sensíveis.")
    with st.form("campaign_form"):
        campaign_text = st.text_area("Texto da vaquinha", height=180, placeholder="Cole aqui a descrição da campanha...")
        campaign_url = st.text_input("Link da campanha (opcional)", placeholder="https://...")
        c1, c2 = st.columns(2)
        with c1:
            beneficiary = st.text_input("Nome do beneficiário (opcional)")
        with c2:
            receiver = st.text_input("Nome que aparece como recebedor do Pix (opcional)")
        submitted = st.form_submit_button("Analisar campanha", type="primary", use_container_width=True)

    if submitted:
        if len(campaign_text.strip()) < 30:
            st.warning("Inclua uma descrição com pelo menos 30 caracteres para realizar a análise.")
        else:
            score, level, color, findings, sim = analyze(campaign_text, campaign_url, beneficiary, receiver)
            st.divider()
            st.subheader("Resultado preliminar")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Índice experimental de sinais", f"{score}/100")
                if color == "red":
                    st.error(f"Nível de atenção: {level}")
                elif color == "orange":
                    st.warning(f"Nível de atenção: {level}")
                else:
                    st.success(f"Nível de atenção: {level}")
            with col2:
                st.markdown("**O que merece atenção**")
                for category, message in findings:
                    st.markdown(f"- **{category}:** {message}")
            st.info("Este protótipo usa regras transparentes e comparação com poucos textos de demonstração. Não verifica a identidade do recebedor, não consulta bancos ou plataformas e não determina se houve crime. Confirme os dados diretamente com a instituição ou beneficiário por canais oficiais antes de doar.")

with tab2:
    st.subheader("O que o protótipo avalia")
    st.markdown("""
    - **Pressão emocional e urgência:** procura expressões que incentivem decisões precipitadas.
    - **Prestação de contas:** verifica se o texto menciona entidade responsável, comprovantes ou transparência.
    - **Consistência de nomes:** compara os nomes digitados para beneficiário e recebedor.
    - **Características básicas do link:** identifica domínio e verifica alguns sinais técnicos simples.
    - **Similaridade textual:** compara o texto enviado com exemplos locais de referência.

    **Próxima evolução:** integrar um modelo de IA para interpretar contexto, adicionar uma base de campanhas verificadas com consentimento e testar o sistema com exemplos rotulados por pessoas.
    """)
    st.warning("Um sinal isolado não significa fraude. Campanhas legítimas podem apresentar urgência, ausência de documentos no texto ou recebedores diferentes do beneficiário.")

with tab3:
    st.subheader("Experimente com um texto fictício")
    sample = st.selectbox("Escolha um exemplo", ["Exemplo com pressão e urgência", "Exemplo com prestação de contas"])
    if sample == "Exemplo com pressão e urgência":
        example = "URGENTE! Ajude agora, só temos poucas horas. Doe imediatamente e compartilhe com todos. Qualquer valor salva vidas!"
    else:
        example = "Estamos arrecadando recursos para compra de alimentos. A ação será organizada pela Associação Comunitária Esperança, com prestação de contas e publicação dos comprovantes."
    st.text_area("Texto de demonstração", value=example, height=130, key="example_text")
    st.caption("Copie o texto para a aba Analisar campanha e faça o teste.")

st.divider()
st.markdown("""
<p class="small-note">DOAÇÃO SEGURA · Protótipo acadêmico/experimental · Versão 0.1<br>
Esta ferramenta não substitui investigação, verificação documental ou orientação jurídica. Não use o resultado como acusação pública.</p>
""", unsafe_allow_html=True)
