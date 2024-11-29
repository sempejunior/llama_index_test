from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, inspect, text
import random

# Conectar ao SQLite
engine = create_engine("sqlite:///articles2.db", future=True)  # Adicionar suporte moderno do SQLAlchemy
metadata = MetaData()

# Verificar tabelas existentes
inspector = inspect(engine)
existing_tables = inspector.get_table_names()

# Criar tabela 'categories' para normalizar as categorias
if 'categories' not in existing_tables:
    categories_table = Table(
        "categories", metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String, unique=True, nullable=False)
    )
    metadata.create_all(engine)
    print("Tabela 'categories' criada com sucesso!")
else:
    categories_table = Table("categories", metadata, autoload_with=engine)
    print("Tabela 'categories' existente encontrada.")

# Criar tabela 'articles' com chave estrangeira 'category_id'
if 'articles' not in existing_tables:
    articles = Table(
        "articles", metadata,
        Column("id", Integer, primary_key=True),
        Column("title", String, nullable=False),
        Column("author", String, nullable=False),
        Column("category_id", Integer, ForeignKey("categories.id"), nullable=False),
        Column("abstract", String)
    )
    metadata.create_all(engine)
    print("Tabela 'articles' criada com sucesso!")
else:
    articles = Table("articles", metadata, autoload_with=engine)
    print("Tabela 'articles' existente encontrada.")

# Criar tabela 'books' com chave estrangeira 'category_id'
if 'books' not in existing_tables:
    books = Table(
        "books", metadata,
        Column("id", Integer, primary_key=True),
        Column("title", String, nullable=False),
        Column("author", String, nullable=False),
        Column("category_id", Integer, ForeignKey("categories.id"), nullable=False),
        Column("summary", String)
    )
    metadata.create_all(engine)
    print("Tabela 'books' criada com sucesso!")
else:
    books = Table("books", metadata, autoload_with=engine)
    print("Tabela 'books' existente encontrada.")

# Dados fictícios
categories = [
    "Artificial Intelligence", "Machine Learning", "Data Science", "Healthcare", "Robotics", "Leadership", "Chess",
    "Soccer", "Tecnologia", "Desenvolvimento de Softwares", "Blockchain", "Cybersecurity", "Quantum Computing",
    "Cloud Computing", "Internet of Things", "Natural Language Processing", "Big Data", "DevOps", "Mobile Development",
    "Game Development", "UI/UX Design", "Augmented Reality", "Virtual Reality", "Digital Transformation",
    "Social Media Analytics", "E-commerce", "Marketing Digital", "Business Intelligence", "Cryptocurrency",
    "Sistemas de Informação", "Engenharia de Software", "Ciência da Computação", "Bioinformática", "Genética"
]

authors = [
    "Carlos Sempé", "José Joselito", "Alice Smith", "Bob Johnson", "Carla Brown", "David Wilson", "Eva Green",
    "John Doe", "Jane Roe", "Thomas Anderson", "Sarah Connor", "Elliot Alderson", "Darlene Alderson", "Angela Moss"
]

# Geradores de dados fictícios
def generate_article(index, category_id):
    """Gera um artigo fictício com base na categoria e autores."""
    return {
        "id": index,
        "title": f"Research on {categories[category_id - 1]} #{index}",
        "author": random.choice(authors),
        "category_id": category_id,
        "abstract": f"This is an abstract about {categories[category_id - 1]}."
    }

def generate_book(index, category_id):
    """Gera um livro fictício com base na categoria e autores."""
    return {
        "id": index,
        "title": f"Book on {categories[category_id - 1]} #{index}",
        "author": random.choice(authors),
        "category_id": category_id,
        "summary": f"This is a summary about {categories[category_id - 1]}."
    }

# Inserir registros nas tabelas
with engine.begin() as conn:
    print("Conexão estabelecida!")

    # Inserir categorias, se necessário
    existing_categories = conn.execute(text("SELECT COUNT(*) FROM categories")).scalar()
    if existing_categories == 0:
        conn.execute(categories_table.insert(), [{"id": i + 1, "name": category} for i, category in enumerate(categories)])
        print("Categorias inseridas com sucesso!")

    # Inserir artigos
    existing_articles = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar()
    if existing_articles == 0:
        articles_data = [generate_article(i, random.randint(1, len(categories))) for i in range(1, 2001)]
        conn.execute(articles.insert(), articles_data)
        print("Artigos inseridos com sucesso!")

    # Inserir livros
    existing_books = conn.execute(text("SELECT COUNT(*) FROM books")).scalar()
    if existing_books == 0:
        books_data = [generate_book(i, random.randint(1, len(categories))) for i in range(1, 1001)]
        conn.execute(books.insert(), books_data)
        print("Livros inseridos com sucesso!")

    # Validar os dados inseridos
    total_articles = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar()
    total_books = conn.execute(text("SELECT COUNT(*) FROM books")).scalar()
    print(f"Total de artigos no banco: {total_articles}")
    print(f"Total de livros no banco: {total_books}")
