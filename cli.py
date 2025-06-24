#!/usr/bin/env python3
"""
Newsletter Generator CLI Tool
Generate professional newsletters from URLs or documents
"""

import os
import sys
import argparse
import json
from pathlib import Path
from newspaper import Article
import pdfplumber
import docx
from transformers import pipeline
import torch
import requests
from bs4 import BeautifulSoup
from llama_cpp import Llama
from tqdm import tqdm

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
            # print(text)
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
            for page in tqdm(pdf.pages, desc="Extracting PDF pages", unit="page"):
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
        text = '\n'.join([para.text for para in tqdm(paras, desc="Extracting DOCX paragraphs", unit="para")])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return None

def generate_newsletter_hf(content, model_name="gpt2", audience="business", api_token=None):
    try:
        generator = pipeline(
            "text-generation",
            model=model_name,
            torch_dtype=None,
            device_map="auto"
        )
        # Generate title using the local model
        title_prompt = (
            f"Write a catchy newsletter headline in one line based on this below article:\n"
            f"{content[:3500]}\n"
        )
        title_result = generator(title_prompt, max_new_tokens=16, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
        title = title_result[0]['generated_text'][len(title_prompt):].replace('\n', ' ').strip()
        # Generate short introduction using the local model
        intro_prompt = (
            f"Write a short, engaging introduction (2-3 sentences) for a newsletter for a {audience} audience. "
            f"Here is the article:\n{content[:3500]}\n"
        )
        intro_result = generator(intro_prompt, max_new_tokens=80, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
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
        for i, chunk in enumerate(tqdm(section_chunks, desc="Generating sections", unit="section")):
            section_prompt = (
                f"Write a detailed, informative newsletter section for a {audience} audience. "
                f"Here is the relevant content:\n{chunk[:800]}\n"
            )
            section_result = generator(section_prompt, max_new_tokens=180, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
            section_text = section_result[0]['generated_text'][len(section_prompt):].replace('\n', ' ').strip()
            sections.append(section_text)
        # Prompt for CTA
        cta_prompt = (
            f"Write a compelling call to action for a newsletter for a {audience} audience. "
            f"Here is the article title: {title}\n"
        )
        cta_result = generator(cta_prompt, max_new_tokens=40, num_return_sequences=1, temperature=0.8, do_sample=True, truncation=True, pad_token_id=generator.tokenizer.eos_token_id, repetition_penalty=1.1, top_p=0.9, top_k=50)
        cta = cta_result[0]['generated_text'][len(cta_prompt):].replace('\n', ' ').strip()
        # Fallback if any part is missing
        if not title or not introduction or not any(sections):
            print("Local model generation didn't produce structured content, using fallback...")
            return create_fallback_newsletter(content)
        return {
            "headline": title,
            "introduction": introduction,
            "sections": sections,
            "cta": cta
        }
    except Exception as e:
        print(f"Error with local model: {e}")
        print("Using fallback newsletter generation...")
        return create_fallback_newsletter(content)

def generate_newsletter(content, model_name="gpt2", audience="business", api_token=None):
    if not content or len(content.strip()) < 50:
        print("Error: Content too short or empty")
        return None
    return generate_newsletter_hf(content, model_name, audience, api_token)

def save_newsletter(newsletter, output_file):
    """Save newsletter to file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(newsletter, f, indent=2, ensure_ascii=False)
        print(f"Newsletter saved to: {output_file}")
    except Exception as e:
        print(f"Error saving newsletter: {e}")

def display_newsletter(newsletter):
    """Display newsletter in a readable format"""
    print("\n" + "="*50)
    print("GENERATED NEWSLETTER")
    print("="*50)
    
    if "raw_output" in newsletter:
        print(newsletter["raw_output"])
        return
    
    print(f"\n📰 {newsletter.get('headline', 'No headline')}")
    print(f"\n{newsletter.get('introduction', 'No introduction')}")
    
    sections = newsletter.get('sections', [])
    for i, section in enumerate(sections, 1):
        print(f"\n📋 Section {i}: {section}")
    
    print(f"\n🎯 Call to Action: {newsletter.get('cta', 'No CTA')}")
    print("="*50)

def interactive_mode():
    """Interactive CLI mode"""
    print("🎉 Welcome to Newsletter Generator CLI!")
    print("Choose an option:")
    print("1. Generate from URL")
    print("2. Generate from file (PDF/DOCX)")
    print("3. Exit")
    print("\nAvailable models:")
    print("1. gpt2 (default, fast)")
    print("2. distilgpt2 (faster)")
    print("3. microsoft/DialoGPT-medium (better quality)")
    model_choice = input("Choose model (1-3, default 1): ").strip() or "1"
    model_map = {
        "1": "gpt2",
        "2": "distilgpt2", 
        "3": "microsoft/DialoGPT-medium"
    }
    model_name = model_map.get(model_choice, "gpt2")
    print("\nAudience options:")
    print("1. Business (default)")
    print("2. Technical")
    audience_choice = input("Choose audience (1-2, default 1): ").strip() or "1"
    audience_map = {"1": "business", "2": "technical"}
    audience = audience_map.get(audience_choice, "business")
    api_token = input("Enter API token (leave empty for default): ").strip() or None
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        if choice == '1':
            url = input("Enter the URL: ").strip()
            if url:
                content = extract_text_from_url(url)
                if content:
                    newsletter = generate_newsletter(content, model_name=model_name, audience=audience, api_token=api_token)
                    if newsletter:
                        display_newsletter(newsletter)
                        save = input("\nSave to file? (y/n): ").strip().lower()
                        if save == 'y':
                            filename = input("Enter filename (default: newsletter.json): ").strip()
                            if not filename:
                                filename = "newsletter.json"
                            save_newsletter(newsletter, filename)
        elif choice == '2':
            filepath = input("Enter file path (PDF or DOCX): ").strip()
            if filepath and os.path.exists(filepath):
                print(f"Processing file: {filepath}")
                if filepath.lower().endswith('.pdf'):
                    content = extract_text_from_pdf(filepath)
                elif filepath.lower().endswith('.docx'):
                    content = extract_text_from_docx(filepath)
                else:
                    print("Error: Only PDF and DOCX files are supported")
                    continue
                if content:
                    print(f"Extracted {len(content)} characters from file")
                    print("Generating newsletter with local model...")
                    newsletter = generate_newsletter(content, model_name=model_name, audience=audience, api_token=api_token)
                    if newsletter:
                        display_newsletter(newsletter)
                        save = input("\nSave to file? (y/n): ").strip().lower()
                        if save == 'y':
                            filename = input("Enter filename (default: newsletter.json): ").strip()
                            if not filename:
                                filename = "newsletter.json"
                            save_newsletter(newsletter, filename)
                else:
                    print("Error: Could not extract content from file")
            else:
                print("Error: File not found")
        elif choice == '3':
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    parser = argparse.ArgumentParser(description='Generate newsletters from URLs or documents using local model')
    parser.add_argument('--url', help='URL to extract content from')
    parser.add_argument('--file', help='PDF or DOCX file to extract content from')
    parser.add_argument('--output', '-o', default='newsletter.json', help='Output file (default: newsletter.json)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--extract-only', action='store_true', help='Only extract content, skip API generation')
    parser.add_argument('--model', default='gpt2', help='Local model name (suggestions: gpt2, distilgpt2, microsoft/DialoGPT-medium)')
    parser.add_argument('--audience', default='business', choices=['business', 'technical'], help='Audience type: business or technical (default: business)')
    parser.add_argument('--api-token', help='Local model API token')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
        return
    
    if not args.url and not args.file:
        print("Error: Please provide either --url or --file argument")
        print("Use --interactive for interactive mode")
        parser.print_help()
        return
    
    content = None
    
    if args.url:
        content = extract_text_from_url(args.url)
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            return
        
        print(f"Processing file: {args.file}")
        if args.file.lower().endswith('.pdf'):
            content = extract_text_from_pdf(args.file)
        elif args.file.lower().endswith('.docx'):
            content = extract_text_from_docx(args.file)
        else:
            print("Error: Only PDF and DOCX files are supported")
            return
        
        if content:
            print(f"Extracted {len(content)} characters from file")
        else:
            print("Error: Could not extract content from file")
            return
    
    if content:
        if args.extract_only:
            print("\n" + "="*50)
            print("EXTRACTED CONTENT")
            print("="*50)
            print(content[:3500] + "..." if len(content) > 3500 else content)
            print("="*50)
            print(f"Content length: {len(content)} characters")
        else:
            newsletter = generate_newsletter(content, model_name=args.model, audience=args.audience, api_token=args.api_token)
            if newsletter:
                display_newsletter(newsletter)
                save_newsletter(newsletter, args.output)

def extract_text_from_url_enhanced(url):
    """Enhanced content extraction with better targeting for different website types"""
    try:
        print(f"Fetching content from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside", "menu", "noscript"]):
            element.decompose()
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Extract meta description
        meta_desc = ""
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_desc_tag:
            meta_desc = meta_desc_tag.get('content', '').strip()
        
        # Try multiple content selectors based on common patterns
        content_selectors = [
            # News/Blog specific
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.story-content',
            '.content-body',
            
            # Generic content areas
            '[role="main"]',
            'main',
            '.main-content',
            '.content',
            '.body-content',
            
            # Specific to common platforms
            '.post-body',
            '.article-body',
            '.story-body',
            '.content-area',
            
            # Fallback selectors
            '.text-content',
            '.article-text',
            '.post-text'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content and len(content.get_text().strip()) > 100:  # Ensure meaningful content
                break
        
        # If no specific content area found, try to find the largest text block
        if not content:
            # Find all paragraphs and divs with substantial text
            text_elements = soup.find_all(['p', 'div', 'section'])
            best_content = None
            max_length = 0
            
            for element in text_elements:
                text = element.get_text().strip()
                if len(text) > max_length and len(text) > 200:  # Minimum meaningful length
                    max_length = len(text)
                    best_content = element
            
            content = best_content
        
        # If still no content, use body
        if not content:
            content = soup.find('body')
        
        if content:
            # Extract text and clean it up
            text = content.get_text(separator='\n', strip=True)
            
            # Clean up extra whitespace and empty lines
            lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 10]
            text = '\n'.join(lines)
            
            # Add title and meta description if available
            full_content = ""
            if title:
                full_content += f"Title: {title}\n\n"
            if meta_desc:
                full_content += f"Summary: {meta_desc}\n\n"
            full_content += text
            
            print(f"Extracted {len(full_content)} characters of content")
            print(f"Title: {title[:100]}..." if len(title) > 100 else f"Title: {title}")
            return full_content
        else:
            print("No content found on the page")
            return None
            
    except Exception as e:
        print(f"Error extracting content from URL: {e}")
        return None

def generate_newsletter_llama(content, model_path="models/llama-2-7b-chat.Q4_K_M.gguf"):
    llm = Llama(model_path=model_path, n_ctx=2048)
    prompt = f"""
Summarize the following content into a professional newsletter with:
- Headline/title
- Short introduction
- 2–3 section summaries
- Call to action at the bottom

Content: {content[:2000]}
"""
    output = llm(prompt, max_tokens=512, stop=["</s>"])
    # Parse output as needed
    return {"raw_output": output["choices"][0]["text"]}

def create_fallback_newsletter(content):
    """Create a basic newsletter structure when local model generation fails, with only 2-3 sections."""
    # Extract title from content if available
    title = ""
    if content.startswith("Title: "):
        title_line = content.split('\n')[0]
        title = title_line.replace("Title: ", "").strip()
        content = '\n'.join(content.split('\n')[2:])
    if not title:
        title = "Newsletter"
    # Extract summary if available
    summary = ""
    if content.startswith("Summary: "):
        summary_line = content.split('\n')[0]
        summary = summary_line.replace("Summary: ", "").strip()
        content = '\n'.join(content.split('\n')[2:])
    if summary:
        introduction = f"{summary} This article provides comprehensive coverage of the topic with detailed analysis and insights that are relevant to our readers."
    else:
        introduction = "This article covers important developments and provides valuable insights on current events and trends that are relevant to our audience."
    # Create sections from content with more detail
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 80]
    # If not enough paragraphs, split by sentences
    if len(paragraphs) < 2:
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 60]
        # Group sentences into sections
        sections = []
        current_section = ""
        for sentence in sentences:
            if len(current_section) < 200:
                current_section += " " + sentence if current_section else sentence
            else:
                if current_section:
                    sections.append(current_section.strip())
                current_section = sentence
        if current_section:
            sections.append(current_section.strip())
        # Ensure we have at least 2 sections
        while len(sections) < 2 and sentences:
            remaining_sentences = [s for s in sentences if s not in ' '.join(sections)]
            if remaining_sentences:
                sections.append(remaining_sentences[0])
            else:
                break
    else:
        sections = paragraphs[:3]
    # Always limit to 2-3 sections
    sections = sections[:3]
    cta = "Read the full article for comprehensive details and stay informed about the latest developments in this important story."
    return {
        "headline": title,
        "introduction": introduction,
        "sections": sections,
        "cta": cta
    }

if __name__ == '__main__':
    main() 