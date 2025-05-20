import os
import json
import re
import sys
from pathlib import Path

def clean_text(text):
    """Clean and normalize text"""
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    # Remove any weird control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    return text.strip()

def extract_document_sections(text):
    """Extract document sections from the combined text file"""
    # Split the text by document separator
    documents = re.split(r'={80}', text)
    
    parsed_documents = []
    
    for doc in documents:
        if not doc.strip():
            continue
        
        # Extract document name
        doc_name_match = re.search(r'DOCUMENT:\s*(.+?)[\n\-]', doc)
        doc_name = doc_name_match.group(1).strip() if doc_name_match else "Unknown"
        
        # Extract pages
        pages = re.split(r'PAGE \d+:', doc)
        
        # Skip the header part
        if len(pages) > 1:
            pages = pages[1:]
        
        # Clean and add pages
        clean_pages = [clean_text(page) for page in pages if clean_text(page)]
        
        # Only add document if it has content
        if clean_pages:
            parsed_documents.append({
                'document_name': doc_name,
                'content': '\n\n'.join(clean_pages)
            })
    
    return parsed_documents

def create_training_jsonl(parsed_documents, output_file='syllabus_training_data.jsonl'):
    """Create a JSONL file for training an AI model"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for doc in parsed_documents:
            # Create a prompt completion pair
            training_item = {
                'prompt': f"Extract information from the following syllabus document:\n\n{doc['document_name']}\n\n",
                'completion': doc['content']
            }
            f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
    
    print(f"Created training data file: {output_file}")
    print(f"Total training examples: {len(parsed_documents)}")

def prepare_qa_format(parsed_documents, output_file='syllabus_qa_data.jsonl'):
    """Create a Q&A format JSONL file for fine-tuning"""
    qa_pairs = []
    
    question_templates = [
        "What is the content of the {doc_name} syllabus?",
        "Provide information about the {doc_name} course.",
        "What topics are covered in the {doc_name} syllabus?",
        "What are the learning objectives of the {doc_name} course?",
        "What is the assessment method for the {doc_name} course?",
        "Describe the units/modules in the {doc_name} course."
    ]
    
    for doc in parsed_documents:
        # Create multiple question-answer pairs for each document
        for template in question_templates:
            question = template.format(doc_name=doc['document_name'])
            
            qa_pairs.append({
                'question': question,
                'answer': doc['content'][:4000]  # Limit answer length for training
            })
    
    # Write to JSONL file
    with open(output_file, 'w', encoding='utf-8') as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    
    print(f"Created Q&A format training data: {output_file}")
    print(f"Total question-answer pairs: {len(qa_pairs)}")

def main():
    # Get input file from command line or use default
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = 'complete_syllabus_text.txt'
        
    # Set output files
    training_output = 'syllabus_training_data.jsonl'
    qa_output = 'syllabus_qa_data.jsonl'
    
    if len(sys.argv) > 2:
        training_output = sys.argv[2]
    
    if len(sys.argv) > 3:
        qa_output = sys.argv[3]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found.")
        print("Make sure to run extract_and_combine.py first.")
        return
    
    print(f"Processing {input_file}...")
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        text = f.read()
    
    # Extract document sections
    parsed_documents = extract_document_sections(text)
    print(f"Extracted {len(parsed_documents)} documents")
    
    # Create training data files
    create_training_jsonl(parsed_documents, output_file=training_output)
    prepare_qa_format(parsed_documents, output_file=qa_output)
    
    print("Done! The files can now be used for AI model training.")

if __name__ == "__main__":
    main() 