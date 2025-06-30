# Newsletter Generator

A professional newsletter generator that creates newsletters from URLs or documents using AI models. The application consists of a Flask backend API and a React frontend.

## Features

- Generate newsletters from URLs or uploaded files (PDF/DOCX)
- Multiple AI model options (GPT-2, DistilGPT-2, GPT-Neo)
- Support for different audience types (Business, Technical)
- Beautiful React UI with drag-and-drop file upload
- Download generated newsletters as JSON or copy to clipboard
- Real-time content extraction from web pages

## Project Structure

```
take_home_asses/
├── app.py                 # Flask backend API
├── cli.py                 # Original CLI version
├── requirements.txt       # Python dependencies
├── frontend/             # React frontend
│   ├── package.json
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── UrlForm.js
│       │   ├── FileUpload.js
│       │   └── NewsletterDisplay.js
│       ├── App.js
│       ├── index.js
│       └── index.css
└── uploads/              # Temporary file upload directory
```

## Setup Instructions

### Backend Setup (Flask)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask backend:**
   ```bash
   python app.py
   ```
   
   The backend will start on `http://localhost:5000`

### Frontend Setup (React)

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   
   The frontend will start on `http://localhost:3000`

### Production Build

To build the React app for production:

```bash
cd frontend
npm run build
```

The built files will be in `frontend/build/` and can be served by the Flask backend.

## API Endpoints

- `POST /api/generate-from-url` - Generate newsletter from URL
- `POST /api/generate-from-file` - Generate newsletter from uploaded file
- `GET /api/models` - Get available AI models
- `GET /api/audiences` - Get available audience types

## Usage

1. Open the application in your browser
2. Choose between generating from URL or uploading a file
3. Select your preferred AI model and target audience
4. Enter the URL or upload a PDF/DOCX file
5. Click "Generate Newsletter" and wait for the AI to process
6. View, copy, or download the generated newsletter

## Supported File Types

- **PDF files** (.pdf)
- **Microsoft Word documents** (.docx)
- **Web URLs** (any accessible webpage)

## AI Models

- **GPT-2** (default, fast) - Good balance of speed and quality
- **DistilGPT-2** (faster) - Optimized for speed
- **GPT-Neo 125M** (better quality) - Enhanced output quality
- **Microsoft Phi-3 Mini** (high quality) - Advanced instruction-following model

## Dependencies

### Backend
- Flask
- Flask-CORS
- BeautifulSoup4
- Requests
- PDFPlumber
- Python-docx
- Transformers
- Torch
- Accelerate

### Frontend
- React 18
- Axios
- React-dropzone

## Development

The application is designed with a clean separation between frontend and backend:

- **Backend**: Flask API with CORS enabled for cross-origin requests
- **Frontend**: React app with modern UI components
- **Communication**: RESTful API calls between frontend and backend

## Troubleshooting

1. **Port conflicts**: Make sure ports 3000 (React) and 5000 (Flask) are available
2. **File upload issues**: Check that the `uploads/` directory exists and is writable
3. **Model loading**: First run may take longer as AI models are downloaded
4. **CORS issues**: Ensure Flask-CORS is properly installed and configured

## License

This project is for educational and demonstration purposes.
