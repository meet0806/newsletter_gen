# Newsletter Generator

This project generates professional email-style newsletters from blog/article URLs or uploaded documents (PDF/DOCX) using AI models.

## Features
- Extracts content from blog/article URLs or uploaded PDF/DOCX files
- Summarizes and structures content into a newsletter (headline, intro, 2–3 sections, CTA)
- Uses local Hugging Face models (no API costs or rate limits)
- **Multi-prompt approach** for better content generation
- **Natural, instruction-like prompts** for higher quality output (no underscores)
- Returns output in JSON format
- **NEW**: CLI tool for easy command-line usage

## Setup
1. Clone the repository or copy the files to your project directory.
2. Create and activate a Python virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

### CLI Tool (Recommended)

#### Interactive Mode
```sh
python cli.py --interactive
```
This will start an interactive menu where you can:
- Choose to generate from URL or file
- Select from different AI models
- Enter URLs or file paths
- Save results to files

#### Command Line Mode
```sh
# Generate from URL (uses gpt2 by default)
python cli.py --url "https://example.com/article" --output my_newsletter.json

# Use a different model
python cli.py --url "https://example.com/article" --model "distilgpt2"

# Generate from PDF file
python cli.py --file document.pdf --output my_newsletter.json

# Generate from DOCX file
python cli.py --file document.docx --output my_newsletter.json

# Extract content only (no AI generation)
python cli.py --file document.pdf --extract-only
```

#### Available Models
- `gpt2` (default) - Good balance of speed and quality
- `distilgpt2` - Faster, smaller model
- `microsoft/DialoGPT-medium` - Better quality, slower

#### CLI Help
```sh
python cli.py --help
```

## Example Output
```json
{
  "headline": "Article Title",
  "introduction": "Summary of the content...",
  "sections": ["Section 1...", "Section 2...", "Section 3..."],
  "cta": "Call to action..."
}
```

## Notes
- Only PDF and DOCX files are supported for uploads.
- Uses local Hugging Face models - no API costs or rate limits.
- The CLI tool is easier to use for testing and quick generation.
- Models are downloaded automatically on first use. 
