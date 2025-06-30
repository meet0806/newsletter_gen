#!/usr/bin/env python3
"""
Newsletter Generator Flask API
Generate professional newsletters from URLs or documents
"""

import os
import json
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from newspaper import Article
import pdfplumber
import docx
from transformers import pipeline
import torch
import requests
from bs4 import BeautifulSoup
from llama_cpp import Llama
from tqdm import tqdm

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_url(url):
    """Extract text content from a URL using BeautifulSoup"""
    try:
        print(f"Fetching content from: {url}")
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try to find the main content area
        content_selectors = [
            'article',
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            'main',
            '.main-content'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        # If no specific content area found, use body
        if not content:
            content = soup.find('body')
        
        if content:
            # Extract text and clean it up
            text = content.get_text(separator='\n', strip=True)
            
            # Clean up extra whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            print(f"Extracted {len(text)} characters of content")
            return text
        else:
            print("No content found on the page")
            return None
        
            
    except Exception as e:
        print(f"Error extracting content from URL: {e}")
        return None

def extract_text_from_pdf(filepath):
    """Extract text from PDF file"""
    try:
        print(f"Extracting text from PDF: {filepath}")
        text = ''
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_docx(filepath):
    """Extract text from DOCX file"""
    try:
        print(f"Extracting text from DOCX: {filepath}")
        doc = docx.Document(filepath)
        paras = list(doc.paragraphs)
        text = '\n'.join([para.text for para in paras])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return None

def generate_newsletter_hf(content, model_name="gpt2", audience="business", api_token=None):
    try:
        # Configure model-specific parameters
        if model_name == "microsoft/Phi-3-mini-4k-instruct":
            # Phi-3 uses different parameters
            generator = pipeline(
                "text-generation",
                model=model_name,
                torch_dtype=None,
                device_map="auto"
            )
            
            # Generate title using Phi-3
            title_prompt = f"<|user|>\nBased on this article content, create a 4-9 word headline for a newsletter:\n\n{content[:1000]}\n\n<|assistant|>\n"
            title_result = generator(title_prompt, max_new_tokens=20, num_return_sequences=1, temperature=0.7, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            title = title_result[0]['generated_text'][len(title_prompt):].replace('\n', ' ').strip()
            
            # Generate introduction using Phi-3
            intro_prompt = f"<|user|>\nWrite a brief introduction for a newsletter based on this article:\n\n{content[:1000]}\n\n<|assistant|>\n"
            intro_result = generator(intro_prompt, max_new_tokens=100, num_return_sequences=1, temperature=0.7, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            introduction = intro_result[0]['generated_text'][len(intro_prompt):].replace('\n', ' ').strip()
            
            # Split content into 3 roughly equal parts for sections
            content_lines = [line for line in content.split('\n') if line.strip()]
            chunk_size = max(1, len(content_lines) // 3)
            section_chunks = [
                '\n'.join(content_lines[i*chunk_size:(i+1)*chunk_size])
                for i in range(3)
            ]
            
            # Generate sections using Phi-3
            sections = []
            for i, chunk in enumerate(section_chunks):
                section_prompt = f"<|user|>\nWrite a newsletter section based on this content:\n\n{chunk[:500]}\n\n<|assistant|>\n"
                section_result = generator(section_prompt, max_new_tokens=200, num_return_sequences=1, temperature=0.7, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
                section_text = section_result[0]['generated_text'][len(section_prompt):].replace('\n', ' ').strip()
                sections.append(section_text)
            
            # Generate CTA using Phi-3
            cta_prompt = f"<|user|>\nWrite a call to action for a newsletter with this headline: {title}\n\n<|assistant|>\n"
            cta_result = generator(cta_prompt, max_new_tokens=50, num_return_sequences=1, temperature=0.7, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            cta = cta_result[0]['generated_text'][len(cta_prompt):].replace('\n', ' ').strip()
            
        else:
            # Original logic for other models (GPT-2, DistilGPT-2, GPT-Neo)
            generator = pipeline(
                "text-generation",
                model=model_name,
                torch_dtype=None,
                device_map="auto"
            )
            # Generate title using the local model
            title_prompt = (
                f"Article: {content[:1000]}\n\n"
                f"Based on the given content give 4-9 words of Headline for newsletter: "
            )
            title_result = generator(title_prompt, max_new_tokens=20, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            title = title_result[0]['generated_text'][len(title_prompt):].replace('\n', ' ').strip()
            # Generate short introduction using the local model
            intro_prompt = (
                f"Article: {content[:1000]}\n\n"
                f"Introduction: This article covers "
            )
            intro_result = generator(intro_prompt, max_new_tokens=100, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            introduction = intro_result[0]['generated_text'][len(intro_prompt):].replace('\n', ' ').strip()
            # Split content into 3 roughly equal parts for sections
            content_lines = [line for line in content.split('\n') if line.strip()]
            chunk_size = max(1, len(content_lines) // 3)
            section_chunks = [
                '\n'.join(content_lines[i*chunk_size:(i+1)*chunk_size])
                for i in range(3)
            ]
            # Prompts for sections
            sections = []
            for i, chunk in enumerate(section_chunks):
                section_prompt = (
                    f"Content: {chunk[:500]}\n\n"
                    f"Section {i+1}: "
                )
                section_result = generator(section_prompt, max_new_tokens=200, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
                section_text = section_result[0]['generated_text'][len(section_prompt):].replace('\n', ' ').strip()
                sections.append(section_text)
            # Prompt for CTA
            cta_prompt = (
                f"Title: {title}\n\n"
                f"Call to Action: "
            )
            cta_result = generator(cta_prompt, max_new_tokens=50, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            cta = cta_result[0]['generated_text'][len(cta_prompt):].replace('\n', ' ').strip()
        
        # Clean up generated content - remove any remaining prompt text
        title = title.split('\n')[0].strip() if title else ""
        introduction = introduction.split('\n')[0].strip() if introduction else ""
        sections = [section.split('\n')[0].strip() for section in sections if section and section.strip()]
        cta = cta.split('\n')[0].strip() if cta else ""
        
        # Check if any part is missing and raise error
        missing_parts = []
        if not title or len(title.strip()) < 5:
            missing_parts.append("title")
        if not introduction or len(introduction.strip()) < 10:
            missing_parts.append("introduction")
        if not sections or len(sections) < 1:
            missing_parts.append("sections")
        elif not any(len(section.strip()) > 20 for section in sections):
            missing_parts.append("valid sections")
            
        if missing_parts:
            print(f"DEBUG - Generated content:")
            print(f"Title: '{title}' (length: {len(title) if title else 0})")
            print(f"Introduction: '{introduction}' (length: {len(introduction) if introduction else 0})")
            print(f"Sections: {len(sections)} sections")
            for i, section in enumerate(sections):
                print(f"  Section {i+1}: '{section[:100]}...' (length: {len(section) if section else 0})")
            raise Exception(f"Local model generation failed to produce: {', '.join(missing_parts)}")
        return {
            "headline": title,
            "introduction": introduction,
            "sections": sections,
            "cta": cta
        }
    except Exception as e:
        print(f"Error with local model: {e}")
        raise

def generate_newsletter(content, model_name="gpt2", audience="business", api_token=None):
    if not content or len(content.strip()) < 50:
        print("Error: Content too short or empty")
        return None
    return generate_newsletter_hf(content, model_name, audience, api_token)

@app.route('/api/generate-from-url', methods=['POST'])
def generate_from_url():
    """Generate newsletter from URL"""
    try:
        data = request.get_json()
        url = data.get('url')
        model_name = data.get('model', 'gpt2')
        audience = data.get('audience', 'business')
        api_token = data.get('api_token')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Extract content from URL
        content = extract_text_from_url(url)
        if not content:
            return jsonify({'error': 'Could not extract content from URL'}), 400
        
        # Generate newsletter
        newsletter = generate_newsletter(content, model_name, audience, api_token)
        if not newsletter:
            return jsonify({'error': 'Failed to generate newsletter'}), 500
        
        return jsonify(newsletter)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-from-file', methods=['POST'])
def generate_from_file():
    """Generate newsletter from uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PDF and DOCX files are allowed'}), 400
        
        # Get other parameters
        model_name = request.form.get('model', 'gpt2')
        audience = request.form.get('audience', 'business')
        api_token = request.form.get('api_token')
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Extract content based on file type
            if filename.lower().endswith('.pdf'):
                content = extract_text_from_pdf(filepath)
            elif filename.lower().endswith('.docx'):
                content = extract_text_from_docx(filepath)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400
            
            if not content:
                return jsonify({'error': 'Could not extract content from file'}), 400
            
            # Generate newsletter
            newsletter = generate_newsletter(content, model_name, audience, api_token)
            if not newsletter:
                return jsonify({'error': 'Failed to generate newsletter'}), 500
            
            return jsonify(newsletter)
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get available models"""
    models = [
        {"id": "gpt2", "name": "GPT-2 (default, fast)"},
        {"id": "distilgpt2", "name": "DistilGPT-2 (faster)"},
        {"id": "EleutherAI/gpt-neo-125M", "name": "GPT-Neo 125M (better quality)"},
        {"id": "microsoft/Phi-3-mini-4k-instruct", "name": "Microsoft Phi-3 Mini (high quality)"}
    ]
    return jsonify(models)

@app.route('/api/audiences', methods=['GET'])
def get_audiences():
    """Get available audience types"""
    audiences = [
        {"id": "business", "name": "Business"},
        {"id": "technical", "name": "Technical"}
    ]
    return jsonify(audiences)

@app.route('/')
def serve_react_app():
    """Serve the React app"""
    return send_from_directory('frontend/build', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from React build"""
    return send_from_directory('frontend/build', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 