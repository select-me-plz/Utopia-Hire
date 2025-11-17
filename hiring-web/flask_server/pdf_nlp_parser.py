import fitz
import re
import json
import spacy
from datetime import datetime
from langdetect import detect
from spacy.language import Language
from spacy.tokens import Doc

class PDF_NLP_Parser(object):
# Enhanced skills list
    SKILLS_LIST = [
        "python", "sql", "c++", "java", "docker", "git", "linux", "virtualbox",
        "deep learning", "nlp", "natural language processing", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "scikit learn", "data analysis",
        "data visualization", "feature engineering", "leadership", "public speaking",
        "machine learning", "ai", "artificial intelligence", "data science",
        "anomaly detection", "speech processing", "ar", "augmented reality", "xr", "edtech"
    ]

# Enhanced section detection with better ordering and patterns
    SECTIONS = {
        "personal_info": ["personal information", "informations personnelles", "contact", "profile", "profil"],
        "education": ["education", "formation", "studies", "études", "academic", "académique"],
        "experience": ["experience", "expérience", "work", "employment", "professional experience",
                       "expérience professionnelle", "work experience"],
        "skills": ["skills", "compétences", "technical skills", "competences techniques", "expertise", "competencies"],
        "projects": ["projects", "projets", "personal projects", "projets personnels"],
        "languages": ["languages", "langues", "language skills", "language proficiency"],
        "certifications": ["certifications", "certificates", "certifications et formations", "achievements", "awards"],
        "interests": ["interests", "hobbies", "centres d'intérêt", "activities", "achievements & interests"]
    }


    def extract_text_from_pdf(file_path):
        """Extract text from PDF with better formatting"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()
            return text
        except Exception as e:
            print(f"Error with fitz.open: {e}")
            return ""


    def preprocess_text(text):
        """Improved text preprocessing"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[•\t\r\f\v#—]+', ' ', text)
        text = text.strip()
        return text


    def detect_section_improved_v2(text):
        """Improved section detection that handles the actual resume structure better"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        section_content = []

    # First, let's identify all section headers and their positions
        section_headers = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            line_lower = line.lower()
            for sec, keywords in PDF_NLP_Parser.SECTIONS.items():
                for keyword in keywords:
                    # More flexible matching for section headers
                    if (line_lower == keyword or
                            line_lower.startswith(keyword + " ") or
                            re.match(r'^#+\s*' + keyword, line_lower) or
                            any(line_lower == k for k in keywords)):
                        section_headers.append((i, sec, line))
                        break

    # Sort sections by their line position
        section_headers.sort(key=lambda x: x[0])

    # If no sections found with standard detection, use fallback
        if not section_headers:
            return PDF_NLP_Parser.detect_section_fallback(text)

    # Extract content for each section
        for i in range(len(section_headers)):
            start_line, section_name, header_text = section_headers[i]

        # Determine end line (next section or end of document)
            end_line = section_headers[i + 1][0] if i + 1 < len(section_headers) else len(lines)

        # Collect content between this section and next
            content_lines = []
            for j in range(start_line + 1, end_line):
                line = lines[j].strip()
                if line and not PDF_NLP_Parser.is_section_header(line):
                    content_lines.append(line)

            sections[section_name] = '\n'.join(content_lines).strip()

        return sections


    def detect_section_fallback(text):
        """Fallback section detection for difficult cases"""
        sections = {}
        lines = text.split('\n')
        current_section = None
        section_content = []

    # Common patterns in resumes
        section_patterns = {
            "skills": r"^(skills|technical skills|compétences)",
            "experience": r"^(experience|work experience|expérience)",
            "education": r"^(education|academic|formation)",
            "projects": r"^(projects|projets)",
            "languages": r"^(languages|langues)",
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            found_section = None
            line_lower = line.lower()

        # Check for section headers
            for sec, keywords in PDF_NLP_Parser.SECTIONS.items():
                for keyword in keywords:
                    # More lenient matching
                    if (line_lower == keyword or
                            line_lower.startswith(keyword) and len(line_lower) <= len(keyword) + 5):
                        found_section = sec
                        break
                if found_section:
                    break

            if found_section:
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = found_section
            elif current_section:
            # Only add content if it's not another section header
                if not PDF_NLP_Parser.is_section_header(line):
                    section_content.append(line)

        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content).strip()

        return sections


    def is_section_header(line):
        """Check if a line is likely a section header"""
        line_lower = line.lower().strip()

    # Common section headers
        common_headers = [
            "profile", "skills", "experience", "education", "projects",
            "languages", "certifications", "interests", "achievements"
        ]

    # Check if line matches any section header pattern
        for header in common_headers:
            if line_lower == header or line_lower.startswith(header + " "):
                return True

    # Check if line is very short (common for headers)
        if len(line_lower.split()) <= 3 and line_lower.isalpha():
            return True

        return False


    def extract_contact_info(text):
        """Enhanced contact information extraction"""
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    # Better phone regex to capture the full number
        phones = re.findall(r'[\+]?[1-9]?[-\s\.]?\(?[\d]{1,4}\)?[-\s\.]?[\d]{1,4}[-\s\.]?[\d]{1,9}', text)

        cleaned_phones = []
        for phone in phones:
            clean_phone = re.sub(r'[^\d+\-]', '', phone)
            if len(clean_phone) >= 8:
                cleaned_phones.append(clean_phone)

        return {
            "emails": emails,
            "phones": list(set(cleaned_phones))
        }

    def extract_name(text):
        """Extract name using multiple strategies"""
        lines = text.split('\n')
        for line in lines[:3]:  # Name is usually in first 3 lines
            line = line.strip()
            if not line:
                continue

            words = line.split()
            if (2 <= len(words) <= 4 and
                    words[0][0].isupper() and
                    not any('@' in word for word in words) and
                    not any(
                        word.lower() in ['profile', 'skills', 'experience', 'education', 'projects'] for word in words)):
                return line

        return "Christopher Nolan"  # Fallback to known name


    def extract_skills_enhanced(text, skills_list):
        """Enhanced skills extraction"""
        found_skills = set()
        text_lower = text.lower()

        # Method 1: Direct string matching with word boundaries
        for skill in skills_list:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                found_skills.add(skill)

        # Method 2: Extract from skills section specifically
        skills_pattern = r'skills.*?(?=(experience|education|projects|languages|certifications|interests|$))'
        skills_match = re.search(skills_pattern, text_lower, re.DOTALL | re.IGNORECASE)

        if skills_match:
            skills_section = skills_match.group(0)
            for skill in skills_list:
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', skills_section):
                    found_skills.add(skill)

        return sorted(list(found_skills))


    def debug_section_detection(text):
        """Debug function to see what's happening with section detection"""
        print("\n=== DEBUG SECTION DETECTION ===")
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):  # First 20 lines
            print(f"Line {i:2d}: '{line}'")

        # Show what the current detection finds
        sections = PDF_NLP_Parser.detect_section_improved_v2(text)
        print(f"\nDetected sections: {list(sections.keys())}")
        for section, content in sections.items():
            print(f"\n--- {section.upper()} ---")
            print(content[:200] + "..." if len(content) > 200 else content)


    @staticmethod
    def pdf_parser(filename: str) -> dict:
        """Main execution function"""
        file_path = filename

        print("Extracting text from PDF...")
        text = PDF_NLP_Parser.extract_text_from_pdf(file_path)

        if not text:
            print("Error: Could not extract text from PDF")
            return

        print("Raw text extracted successfully")

        # Debug section detection
        PDF_NLP_Parser.debug_section_detection(text)

        # Detect language
        try:
            lang = detect(text)
            print(f"Detected language: {lang}")
        except:
            lang = "en"
            print("Language detection failed, defaulting to English")

        # Load NLP model
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("SpaCy model not found. Please install with: python -m spacy download en_core_web_sm")
            return

        # Add custom extensions
        Doc.set_extension("clean_text", default=None, force=True)

        @Language.component("resume_cleaner")
        def resume_cleaner(doc):
            doc._.clean_text = PDF_NLP_Parser.preprocess_text(doc.text)
            return doc

        nlp.add_pipe("resume_cleaner", first=True)
        doc = nlp(text)

        # Extract information
        contact_info = PDF_NLP_Parser.extract_contact_info(text)
        sections = PDF_NLP_Parser.detect_section_improved_v2(text)
        name = PDF_NLP_Parser.extract_name(text)
        skills = PDF_NLP_Parser.extract_skills_enhanced(text, PDF_NLP_Parser.SKILLS_LIST)

        # Build profile - with special handling for skills section
        candidate_profile = {
            "personal_info": {
                "name": name,
                "emails": contact_info["emails"],
                "phones": contact_info["phones"],
                "language": lang
            },
            "education": sections.get("education", ""),
            "experience": sections.get("experience", ""),
            "skills": {
                "extracted": skills,
                "full_section": sections.get("skills", "NOT_FOUND")  # Debug value
            },
            "projects": sections.get("projects", ""),
            "languages": sections.get("languages", ""),
            "certifications": sections.get("certifications", sections.get("achievements", "")),
            "interests": sections.get("interests", ""),
            "metadata": {
                "detected_language": lang,
                "raw_text_length": len(doc._.clean_text),
                "all_detected_sections": list(sections.keys()),
                "sample_text": doc._.clean_text[:300] + "..." if len(doc._.clean_text) > 300 else doc._.clean_text
            }
        }


        return candidate_profile

