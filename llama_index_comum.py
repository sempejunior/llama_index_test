import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from llama_index.core.indices.struct_store.sql import SQLQueryMode
from llama_index.core import SQLDatabase
from llama_index.core.indices.struct_store import SQLStructStoreIndex
from llama_index.llms.openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")

if not OPENAI_API_KEY or not DATABASE_URI:
    raise ValueError("As variáveis OPENAI_API_KEY e DATABASE_URI precisam estar configuradas no .env")

llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

engine = create_engine(DATABASE_URI)
sql_database = SQLDatabase(engine)

index = SQLStructStoreIndex(
    sql_database=sql_database,  # Conexão com o banco
    include_tables=["articles", "books", "categories"],  # Tabelas a serem incluídas no índice
    table_metadata={
        "articles": "Tabela que armazena artigos com título, autor, categoria e resumo.",
        "books": "Tabela que armazena livros com título, autor, categoria e sumário.",
        "categories": "Tabela que contém as categorias disponíveis para artigos e livros.",
    }
)

query_engine = index.as_query_engine(llm=llm, query_mode=SQLQueryMode.NL)


def ask_question(question: str):
    """
    Faz uma pergunta em linguagem natural, gera uma consulta SQL e executa no banco.
    """
    print(f"\nPergunta: {question}")
    try:
        response = query_engine.query(question)
        print(f"\nResposta:\n{response.response}")
        print(f"\nQuery Executada: {response.metadata.get('sql_query')}")
        print(f"\nResultado do Banco de Dados: {response.metadata.get('result')}")
        print("__________________________________________________________________________")
    except Exception as e:
        print(f"\nErro ao executar consulta: {e}")


if __name__ == "__main__":
    ask_question("Quais são os títulos dos artigos na categoria 'Tecnologia'?")
    ask_question("Quais são todos os artigos e livros escritos por Carlos Sempé?")
    ask_question("Quantos artigos e livros existem em cada categoria?")
    ask_question("Quais livros e artigos foram escritos por Carlos Sempé sobre Chess")