import io
from typing import Union
import PyPDF2
from docx import Document


class FileParser:
    """
    Parses different file formats and extracts text content
    """
    
    def parse_pdf(self, file_content: bytes) -> str:
        """
        Extract text from PDF file
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")
    
    def parse_docx(self, file_content: bytes) -> str:
        """
        Extract text from DOCX file
        """
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")
    
    def parse_txt(self, file_content: bytes) -> str:
        """
        Extract text from TXT file
        """
        try:
            return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            raise Exception(f"Error parsing TXT: {str(e)}")
