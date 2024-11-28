import os

from llama_index.core.indices.struct_store.sql import SQLQueryMode
from sqlalchemy import create_engine
from dotenv import load_dotenv
from llama_index.core import SQLDatabase
from llama_index.core.indices.struct_store import SQLStructStoreIndex
from llama_index.llms.openai import OpenAI


# Carregar variáveis do arquivo .env
load_dotenv()

# Configuração da chave de API da OpenAI e banco de dados
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")

if not OPENAI_API_KEY or not DATABASE_URI:
    raise ValueError("As variáveis OPENAI_API_KEY e DATABASE_URI precisam estar configuradas no .env")

# Configuração da OpenAI LLM
llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

# Conexão com o banco de dados SQL usando o LlamaIndex
engine = create_engine(DATABASE_URI)
sql_database = SQLDatabase(engine)

# Criar índice estruturado com base nas tabelas do banco
index = SQLStructStoreIndex(
    sql_database=sql_database,  # Conexão com o banco
)

# Configurar o Query Engine
query_engine = index.as_query_engine(llm=llm, query_mode=SQLQueryMode.NL)

# Função principal para realizar perguntas e consultas
def ask_question(question: str):
    """
    Faz uma pergunta em linguagem natural, gera uma consulta SQL e executa no banco.
    """
    print(f"\nPergunta: {question}")
    response = query_engine.query(question)  # O Query Engine usa LlamaIndex + LLM
    print(f"\nResposta:\n{response.response}")
    print(f"\nQuery Executada: {response.metadata.get('sql_query')}")  # Mostra a query gerada pelo LLM
    print(f"\nResultado do Banco de Dados: {response.metadata.get('result')}")  # Mostra os resultados brutos do banco


# Exemplo de Pergunta
ask_question("Quais são os títulos dos artigos na categoria 'Tecnologia'?")