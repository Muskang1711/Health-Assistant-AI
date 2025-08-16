import pytesseract
from PIL import Image
import PyPDF2
import io
from fastapi import UploadFile
import boto3
from typing import Optional
# AWS Textract client (optional for scalability)
textract = boto3.client('textract', region_name='us-east-1') if boto3.Session().get_credentials() else None

async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    if file.filename.endswith(('.jpg', '.png', '.jpeg')):
        # Process image (X-ray or receipt)
        image = Image.open(io.BytesIO(content))
        if textract:
            # AWS Textract for scalability
            response = textract.detect_document_text(Document={'Bytes': content})
            text = ' '.join([item['Text'] for item in response['Blocks'] if item['BlockType'] == 'LINE'])
        else:
            # Local pytesseract
            text = pytesseract.image_to_string(image)
    elif file.filename.endswith('.pdf'):
        # Process PDF (e.g., doctor receipt)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ' '.join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
    else:
        raise ValueError("Unsupported file type")
    return text.strip() or "No text extracted"