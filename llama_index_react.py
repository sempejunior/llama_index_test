
import os
import webbrowser
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv
from llama_index.core import SQLDatabase
from llama_index.core.agent import ReActAgent
from llama_index.core.indices import SQLStructStoreIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine

from tools.pandas_tool import PandasPlotTool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URI = os.getenv("DATABASE_URI")

if not OPENAI_API_KEY or not DATABASE_URI:
    raise ValueError("As variáveis OPENAI_API_KEY e DATABASE_URI precisam estar configuradas no .env")

llm = OpenAI(api_key=OPENAI_API_KEY, model='gpt-4', temperature=0.5)

engine = create_engine(DATABASE_URI)
sql_database = SQLDatabase(engine)

index = SQLStructStoreIndex(
    sql_database=sql_database,
    include_tables=["articles", "books", "categories"],
    table_metadata={
        "articles": "Tabela que armazena artigos com título, autor, categoria e resumo. Colunas: id, title, author, category_id, abstract.",
        "books": "Tabela que armazena livros com título, autor, categoria e sumário. Colunas: id, title, author, category_id, summary.",
        "categories": "Tabela que contém as categorias disponíveis. Colunas: id, name.",
    }
)

query_engine = index.as_query_engine()

query_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="query_engine_tool",
    description="Ferramenta para consultar livros, artigos e categorias no banco de dados SQL",
    return_direct=False,
)

pandas_plot_tool = PandasPlotTool()

react_agent = ReActAgent.from_tools(
    tools=[query_tool, pandas_plot_tool],
    llm=llm,
    verbose=True
)

def display_graph(image_base64: str):
    """Exibe o gráfico gerado no navegador."""
    with NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        html_content = f'<img src="{image_base64}" alt="Gráfico Gerado">'
        tmp.write(html_content.encode("utf-8"))
        webbrowser.open(f"file://{tmp.name}")

def ask_question_with_agent(question: str):
    """Faz uma pergunta ao agente e exibe a resposta."""
    print(f"\n=== Pergunta: {question} ===\n")
    try:
        response = react_agent.chat(question)

        print("=== Resposta do Agente ===")
        print(response.response)

        for source in response.sources:
            if "Gráfico gerado com sucesso." in source.content:

                image_base64 = source.raw_output
                print("\nGráfico gerado com sucesso. Exibindo...\n")
                display_graph(f"data:image/png;base64,{image_base64}")
                return

        print("\nNenhum gráfico gerado.\n")

    except Exception as e:
        print(f"\nErro ao executar consulta com o agente: {e}")


# Exemplo de Perguntas
if __name__ == "__main__":

    ask_question_with_agent("Quais são os títulos dos artigos na categoria 'Tecnologia'?")
    ask_question_with_agent("Quero um gráfico que represente os top 5 autores "
                            "com maior número de artigos publicados em artigos diferentes'?")
    ask_question_with_agent("Mostre um gráfico da quantidade de artigos por categoria.")
