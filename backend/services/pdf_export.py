import io
import logging


try:
    from weasyprint import HTML, CSS
    WEASYPRINT_INSTALLED = True
    
except ImportError:
    WEASYPRINT_INSTALLED = False
    
logger = logging.getLogger('ats_resume_scorer')

def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    if not WEASYPRINT_INSTALLED:
        raise ImportError("WeasyPrint is not Installed. PDF generation unavailabel")
    
    documents = []
    
    
    # render all 3 html strings to weasyprint document objects
    
    for name, html_str in html_docs.items():
        doc = HTML(string=html_str).render()
        documents.append(doc)
        
    
    # Merge them into the first documents
    first_doc = docuemnts[0]
    for other_doc in documents[1:]:
        for page in other_doc.pages:
            first_doc.pages.append(page)
            
    # write combined pdf bytes
    pdf_bytes = first_doc.write_pdf()
    return pdf_bytes


    