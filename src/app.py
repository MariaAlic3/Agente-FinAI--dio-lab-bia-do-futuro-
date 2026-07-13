import os
import json
import pandas as pd
import streamlit as st
import requests

# ==========================================
# # ============ CONFIGURAÇÃO ============
# ==========================================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "gpt-oss"

# ==========================================
# 1. CARREGAR DADOS E MONTAR CONTEXTO 
# ==========================================
# Ajuste de caminho para garantir que encontre a pasta 'data' rodando de dentro de 'src'
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

try:
    # =========== CARREGAR DADOS  ============
    perfil = json.load(open(os.path.join(DATA_DIR, "perfil_investidor.json"), encoding="utf-8"))
    transacoes = pd.read_csv(os.path.join(DATA_DIR, "transacoes.csv"))
    historico = pd.read_csv(os.path.join(DATA_DIR, "historico_atendimento.csv"))
    produtos = json.load(open(os.path.join(DATA_DIR, "produtos_financeiros.json"), encoding="utf-8"))

    # ======= MONTAR CONTEXTO ========
    contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""
    nome_cliente = perfil['nome']
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    contexto = ""
    nome_cliente = "Usuário"

# ==============================================================================
# 2. CONFIGURAÇÃO DA IA & CHAMAR OLLAMA 
# ==============================================================================

SYSTEM_PROMPT = """Você é o FinAI, um assistente virtual e mentor financeiro inteligente. 
Seu objetivo principal é atuar como um mentor financeiro empático, analisando o orçamento e guiando o cliente no planejamento de suas metas ativas de forma estritamente técnica, acolhedora e sem julgamentos.

REGRAS:
1. POSTURA SEM JULGAMENTOS: Nunca critique os gastos do cliente. Trate tudo de forma matemática, técnica e acolhedora. Nunca use palavras como "errado" ou "irresponsável".
2. GROUNDING: Responda usando apenas os dados fornecidos. Não invente informações.
3. FRASE DE ESCAPE: Se o usuário perguntar algo fora de finanças (como previsão do tempo ou política), responda exatamente: "Desculpe, como seu assistente FinAI, posso ajudar você apenas com o planejamento de suas metas e análise do seu orçamento atual. Vamos voltar ao seu plano?"
4. Seja conciso. Use tópicos curtos em Markdown.
5. Linguagem simples e direta. Evite jargões financeiros complexos."""

def perguntar(msg):
    # Montagem do prompt 
    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO DO CLIENTE:
{contexto}

Pergunta: {msg}"""
    
    try:
        # Requisição 
        r = requests.post(OLLAMA_URL, json={"model": MODELO, "prompt": prompt, "stream": False}, timeout=None)
        if r.status_code == 200:
            return r.json()['response']
        return f"Erro no Ollama: Status {r.status_code}"
    except requests.exceptions.ConnectionError:
        return "⚠️ Erro: O Ollama não está rodando. Inicie-o no terminal usando `ollama run gpt-oss` antes de testar."

# ==============================================================================
# 3. INTERFACE DO CHAT (STREAMLIT)
# ==============================================================================

st.set_page_config(page_title="FinAI - Mentor Financeiro", page_icon="💰", layout="centered")

st.title("💰 FinAI — Seu Mentor Financeiro")
st.markdown(f"Conectado com sucesso à base de dados do cliente **{nome_cliente}**.")
st.divider()

# Histórico de mensagens da sessão para manter a conversa fluida na tela
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"Olá, {nome_cliente}! Sou o FinAI. Como posso te ajudar com suas finanças e análise de gastos hoje?"}
    ]

# Exibe mensagens antigas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de novas mensagens (Adaptado para o formato de chat mantendo a chamada da função)
if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    with st.chat_message("user"):
        st.markdown(pergunta)
    st.session_state.messages.append({"role": "user", "content": pergunta})

    # Resposta da IA usando função estruturada
    with st.chat_message("assistant"):
        with st.spinner("..."):
            resposta = perguntar(pergunta)
            st.markdown(resposta)
            
    st.session_state.messages.append({"role": "assistant", "content": resposta})