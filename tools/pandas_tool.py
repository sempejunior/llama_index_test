# pandas_tool.py

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import json

from llama_index.core.tools import BaseTool, ToolMetadata, ToolOutput


class PandasPlotTool(BaseTool):
    """Tool para geração de gráficos com Pandas e Matplotlib."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="pandas_plot_tool",
            description=(
                "Use esta ferramenta para criar um gráfico a partir de dados tabulares. "
                "Forneça os dados como uma lista de dicionários ou um DataFrame em formato JSON. "
                "Exemplo de input: '{\"data\": [...], \"graph_type\": \"bar\", \"x_column\": \"categoria\", \"y_column\": \"contagem\"}'. "
                "Se não especificar 'graph_type', 'x_column' ou 'y_column', a ferramenta tentará escolher automaticamente."
            ),
        )

    def __call__(self, tool_input: str) -> ToolOutput:
        """Recebe os dados e parâmetros do gráfico, e retorna a imagem base64."""
        try:
            # Parse tool_input como JSON
            input_dict = json.loads(tool_input)

            data = input_dict.get("data")
            graph_type = input_dict.get("graph_type", None)
            x_column = input_dict.get("x_column", None)
            y_column = input_dict.get("y_column", None)

            if not data:
                return ToolOutput(
                    content="Parâmetros insuficientes para criar o gráfico. 'data' é obrigatório.",
                    tool_name=self.metadata.name,
                    raw_input=input_dict,
                    raw_output=None,
                    is_error=True
                )

            df = pd.DataFrame(data)

            # Se não forem fornecidos, escolher automaticamente
            if not x_column or not y_column:
                numeric_columns = df.select_dtypes(include='number').columns.tolist()
                if len(numeric_columns) >= 2:
                    x_column = numeric_columns[0]
                    y_column = numeric_columns[1]
                elif len(numeric_columns) == 1:
                    y_column = numeric_columns[0]
                    x_column = df.columns[0] if df.columns[0] != y_column else df.columns[1]
                else:
                    return ToolOutput(
                        content="Não foi possível determinar colunas numéricas para x e y.",
                        tool_name=self.metadata.name,
                        raw_input=input_dict,
                        raw_output=None,
                        is_error=True
                    )

            if not graph_type:
                graph_type = 'bar'  # Padrão para 'bar'

            return self._process(df, graph_type, x_column, y_column, input_dict)
        except Exception as e:
            return ToolOutput(
                content=f"Erro ao criar gráfico: {e}",
                tool_name=self.metadata.name,
                raw_input=tool_input,
                raw_output=None,
                is_error=True
            )

    async def arun(self, tool_input: str) -> ToolOutput:
        """Versão assíncrona não implementada."""
        raise NotImplementedError("PandasPlotTool não suporta execução assíncrona")

    def _process(self, df: pd.DataFrame, graph_type: str, x_column: str, y_column: str, input_dict: dict) -> ToolOutput:
        """Processa os dados e gera um gráfico."""
        try:
            plt.figure(figsize=(10, 6))

            # Gera o gráfico com base no tipo
            if graph_type == "bar":
                df.plot(kind="bar", x=x_column, y=y_column, legend=False, ax=plt.gca())
            elif graph_type == "line":
                df.plot(kind="line", x=x_column, y=y_column, legend=False, ax=plt.gca())
            elif graph_type == "pie":
                df.set_index(x_column)[y_column].plot(kind="pie", autopct="%1.1f%%", ax=plt.gca())
            else:
                return ToolOutput(
                    content=f"Tipo de gráfico '{graph_type}' não suportado.",
                    tool_name=self.metadata.name,
                    raw_input=input_dict,
                    raw_output=None,
                    is_error=True
                )

            plt.title(f"Gráfico de {graph_type} - {y_column} por {x_column}")
            plt.tight_layout()

            # Salvar gráfico como imagem base64
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format="png")
            plt.close()
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")

            # Retornar a mensagem sem a string base64 completa
            return ToolOutput(
                content="Gráfico gerado com sucesso.",
                tool_name=self.metadata.name,
                raw_input=input_dict,
                raw_output=img_base64,
                is_error=False
            )
        except Exception as e:
            return ToolOutput(
                content=f"Erro ao gerar gráfico: {e}",
                tool_name=self.metadata.name,
                raw_input=input_dict,
                raw_output=None,
                is_error=True
            )
