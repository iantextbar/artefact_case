from typing import Annotated

from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel
from sqlalchemy import text

from src.utils.settings import Settings
from src.utils.storage import Db

# Global variables
settings = Settings()
DB = Db()

# Products

# Check product by name, categoria and/ or price
@tool
def search_product_name_category_price(name_or_category: str = None, max_price: float = None) -> str:
    """
    Busca instrumentos musicais na tabela de produtos. Permite buscar o produto pelo nome, categoria do
    produto (Guitarra, Violão, Teclado etc.) ou pelo preço máximo (buscar produtos abaixo de R$500.00).
    Use essa ferramenta, sempre que o cliente fizer perguntas relacionadas à existência de um produto.
    [CRÍTICO] Se for buscar por categoria, use EXATAMENTE um destes termos: 'Guitarras', 'Violões', 'Teclados e Pianos',
          'Baixos', 'Baterias e Percussão', 'Instrumentos de Sopro (Madeiras)', 'Instrumentos de Sopro (Metais)', 'Cordas Orquestrais', 'Ukuleles'.
    Sempre converta termos informais dos clientes para essas categorias estruturadas.
    
    Argumentos:
        name_or_category: nome do modelo ou uma das categorias válidas ('Guitarras', 'Violões', 'Teclados e Pianos',
          'Baixos', 'Baterias e Percussão', 'Instrumentos de Sopro (Madeiras)', 'Instrumentos de Sopro (Metais)', 'Cordas Orquestrais', 'Ukuleles')
        max_price: preço máximo do produto, como R$650.00
    """

    query = """
        SELECT p.name, p.price_brl, p.stock_quantity, p.status, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        WHERE 1=1
    """

    params = {}

    if name_or_category:
        query += " AND (p.name LIKE :term OR c.name LIKE :term)"
        term = f"%{name_or_category}%"
        params['term'] = term
    if max_price:
        query += " AND p.price_brl <= :max_price"
        params['max_price'] = max_price

    try:
        with DB.get_session() as session:
            res = session.execute(text(query), params)
            rows = res.fetchall()

            if not rows:
                return "Não foi encontrado nenhum instrumento com essas especificações na base de dados"

            results = []
            for row in rows:
                prod_name, price, qtt, status, cat_name = row
                results.append(f"{prod_name} ({cat_name}) - Preço: R$ {price} | Estoque: {qtt} - Status no Estoque: {status}")

            return "\n".join(results)
        
    except Exception as e:
        return f"Erro ao consultar o banco de dados de produtos: {str(e)}"

# Order
@tool
def search_order_status(config: RunnableConfig) -> str:
    """
    Busca informações sobre a situação, histórico e rastreamento de TODOS os pedidos do cliente atual.
    Use essa ferramenta sempre que o cliente perguntar 'onde está meu pedido', 'qual o status da minha compra'
    ou quiser ver o histórico de pedidos dele.
    """
    
    configurable = config.get("configurable", {})
    telephone_number = configurable.get("client_phone")
    
    if not telephone_number:
        return "Erro interno de segurança: Identificador do cliente não foi propagado corretamente."

    query = """
        SELECT o.order_date, o.total_brl, o.status, o.estimated_delivery, c.phone
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE c.phone = :telephone_number
    """

    try:
        with DB.get_session() as session:
            result = session.execute(
                text(query), 
                {"telephone_number": telephone_number}
            )
            rows = result.fetchall()

            if not rows:
                return "Não encontrei nenhum pedido vinculado ao seu número de telefone."

            results = []
            for row in rows:
                order_date, total_brl, status, est_del, phone = row
                results.append(f"Para Telefone: {phone} | Pedido feito em: {order_date} |\n"
                               f"Status: {status} | Estimativa de Entrega: {est_del} | Valor do Pedido: {total_brl}")

            return "\n".join(results)
        
    except Exception as e:
        return f"Erro ao consultar o banco de dados de produtos: {str(e)}"
