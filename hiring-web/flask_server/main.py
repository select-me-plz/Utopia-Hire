from linkedin_scrapper import LinkedinScrapper
from pdf_nlp_parser import PDF_NLP_Parser as pnp
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:4200", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

linkedin_scrap = LinkedinScrapper()

@app.route('/api/jobs', methods=['POST'])
def get_jobs():
    data = request.get_json(force=True)
    job_title = data['job_title']
    job_location = data['job_location']
    pages_number = data['pages_number'] if 'pages_number' in data else 1
    max_jobs = data['max_jobs'] if 'max_jobs' in data else 5

    linkedin_jobs = LinkedinScrapper.scrape_linkedin_jobs(job_title, job_location, pages_number, max_jobs)
    linkedin_jobs = LinkedinScrapper.clean_jobs(linkedin_jobs)
    #return jsonify({"found_jobs": linkedin_jobs}, {"count": len(linkedin_jobs)})
    return jsonify(linkedin_jobs)

@app.route('/api/pdf_parse', methods=['POST'])
def get_pdf_nlp():
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    if file and '.pdf' in file.filename:
        # Create temp directory if it doesn't exist
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)
        try:
            response = jsonify(pnp.pdf_parser(file_path))
            return response
        except Exception as e:
            return jsonify({'error': f'Error processing PDF: {str(e)}'})
        finally:
            # Clean up: remove the file after processing
            try:
                os.remove(file_path)
            except OSError:
                pass  # File might already be deleted
    else:
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
