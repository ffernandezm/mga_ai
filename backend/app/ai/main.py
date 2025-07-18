from .models.document import Document
from .models.query_processor import QueryProcessor

async def main(problem_tree_json,message):
    pdf_path = "/home/ffernandez/fastapi/app/ai/data/Documento_conceptual_2023.pdf"
    doc = Document(pdf_path)
    query_processor = QueryProcessor(doc.get_text())
    
    #query = "Como especialista en gestion de proyectos quiero que me ayudes a organizar el árbol de problemas según la metodología generla ajustable (MGA) \n"
    query = "contexto del árbol de problemas: \n"
    query += problem_tree_json
    query += "responde de forma puntual al siguiente mensaje: \n"
    query += message+'\n'
    
    response = await query_processor.ask(query)
    print(response)
    return response