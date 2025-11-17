# Flask Server

This is the Flask-based server for the Hiring Web Application. It provides additional functionalities such as CV parsing and LinkedIn scraping.

## Features
- CV parsing using NLP
- LinkedIn scraping for candidate data

## Installation
1. Navigate to the `flask_server` directory:
   ```bash
   cd flask_server
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server
Start the Flask server:
```bash
python main.py
```

## Dependencies
- Flask
- Flask-CORS
- SpaCy
- PyMuPDF
- BeautifulSoup

## Notes
- Ensure you have the required Python version and dependencies installed.
- For LinkedIn scraping, additional setup may be required (e.g., Playwright).