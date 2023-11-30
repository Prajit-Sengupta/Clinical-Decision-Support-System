import PyPDF2
import re

def extract_text_from_pdf(pdf_file_path):
    try:
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            if len(pdf_reader.pages) == 0:
                return "The PDF file is empty."

            extracted_text = ''
            for page in pdf_reader.pages:
                extracted_text += page.extract_text()

            return find_tb_status(extracted_text)
    except FileNotFoundError:
        return f"Error: The file '{pdf_file_path}' not found."
    except Exception as e:
        return f"Error: {str(e)}"

def find_tb_status(text_data):
    # Define regular expressions to search for specific patterns
    tb_positive_patterns = [
        r'\b(tb\s*positive)\b',
        r'\b(\s*positive\s*Tuberculosis)\b',
        r'\b(tb[\w\s]*pos(itive)?)\b',
        r'\b(positive for tb)\b',
        r'\b(active tb)\b',
        r'\b(tb infection detected)\b',
        r'\b(tb present)\b',
        r'\b(tb\s*diagnosed)\b',
        r'\b(tb\s*infection)\b',
    ]
    
    tb_negative_patterns = [
        r'\b(tb\s*negative)\b',
        r'\b(tb[\w\s]*neg(ative)?)\b',
        r'\b(negative for tb)\b',
        r'\b(no active tb)\b',
        r'\b(no tb infection detected)\b',
        r'\b(no evidence of tb)\b',
        r'\b(tb\s*not\s*detected)\b',
    ]

    # Check for positive patterns
    for pattern in tb_positive_patterns:
        if re.search(pattern, text_data, re.IGNORECASE):
            return 'TB Positive'

    # Check for negative patterns
    for pattern in tb_negative_patterns:
        if re.search(pattern, text_data, re.IGNORECASE):
            return 'TB Negative'

    return 'TB status not mentioned or unclear'

# Example usage:
pdf_file_path = "C://Users//lookf//OneDrive//Desktop//New folder//static//tb-prescriptions//1.pdf"
extracted_text = extract_text_from_pdf(pdf_file_path)
print(extracted_text)

