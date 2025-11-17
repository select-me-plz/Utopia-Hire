# Utopia-Hire

### 1. Introduction
This project presents a modular, AI-driven platform designed to support candidates throughout the job-seeking process using advanced natural language processing and model-orchestration techniques. The solution integrates resume evaluation, job-matching intelligence, interview simulation, and career advisory features into a unified, secure system.

The application follows a privacy-by-design, security-by-design, and user-centric methodology, ensuring high accuracy, transparency, and fairness while relying on an innovative multi-adapter AI architecture.

### 2. High-Level Features & Functional Components
#### 2.1 Resume Reviewer & Rewriter
- Processes structured resume data.
- Uses a fine-tuned LoRA adapter to:
  - Evaluate resume quality.
  - Score clarity, consistency, and relevance.
  - Suggest corrections, rewriting, and improvement guidance.
- Outputs structured, interpretable feedback.

#### 2.2 AI Interviewer & Candidate Profiler
- A specialized conversational adapter simulates real-world recruiter behavior.
- Identifies strengths, weaknesses, communication patterns, and role fit.
- Provides insights based on typical hiring practices and competency models.

#### 2.3 Job Matcher
- Takes user resume data and available job listings.
- Produces:
  - The most relevant job offer.
  - Matching rationale.
  - Confidence score.
- Enhances regional job relevance through contextual embeddings and domain-finetuned logic.

#### 2.4 Footprint Scanner (Public Profile Analysis)
- Optional module designed to analyze publicly accessible digital presence:
  - Activity signals from LinkedIn or data that the user directly provides.
  - Skills inferred from wording, achievements, and professional footprints.
- Designed under strict compliance:
  - Only uses data the user voluntarily submits.
  - No unauthorized scraping or access.
  - Transparency guaranteed.

#### 2.5 Career Insights Report
- Consolidates insights from all modules:
  - Competencies analysis
  - Growth opportunities
  - Job alignment
  - Market positioning recommendations
- Fully generated through structured prompts ensuring clarity and strategic value.

### 3. System Design & Modular Architecture
#### 3.1 Overview
```
User (Angular App)
        ↓
API Gateway & Router (Flask)
        ↓
Intent Manager
        ↓
-----------------------------------
| Base Model (Phi-3 Mini)         |
|  - General Chat                 |
|  - Career Advisor Mode          |
-----------------------------------
        ↓
LoRA Adapter Layer
| resume_eval     |
| job_match       |
| recruiter_dialog|
| latex_resume    |
-----------------------------------
        ↓
Structured Outputs
```

#### 3.2 Key Architectural Innovations
**A. Dynamic LoRA Adapter Switching**
- Adapters load on-demand, without reloading the base model.
- Achieves high performance using low-resource quantization techniques.
- Greatly reduces computational cost and memory footprint.

**B. Unified Router for Intelligent Task Allocation**
- A central intent manager classifies user queries.
- Automatically switches between:
  - Base model (general conversation)
  - Base model in career expert mode
  - Specialized LoRA adapters
- Ensures user receives the "right kind" of intelligence with minimal friction.

**C. Career-Expert Prompt Layer**
- A specialized prompt injects:
  - Hiring best practices
  - Professional development strategies
  - Role-based advice
- Ensures consistent, expert-grade guidance.

**D. Composable Output Pipeline**
- Each model produces structured outputs in JSON.
- The system normalizes and transforms outputs into human-readable responses.
- Strong separation between reasoning and presentation layers.

### 4. Technical Workflow
#### 4.1 Data Flow
1. User submits message through Angular frontend.
2. API receives request, determines required module (via intent detection).
3. Model Manager triggers:
   - Base model or
   - Specific LoRA adapter
4. Model inference occurs, returning structured insights.
5. Response normalization & security filtering (to avoid hallucinated sensitive info).
6. Frontend presents clear guidance.

#### 4.2 Testing Methodology
The system has been tested with:
- Real and synthetic resumes
- Simulated job postings scraped from public sources
- Manually generated interview dialogues
- Mocked professional footprint data

These tests were used to measure:
- Accuracy of job matching
- Consistency of resume scoring
- Reliability of recruiter simulation
- Clarity of generated career insights

### 5. Security, Integrity & Ethical Considerations
#### 5.1 Privacy-by-Design
- No user data is stored permanently unless explicitly allowed.
- Resume and profile data processed only in-memory.
- No unauthorized scraping.
- Clear user consent for footprint scanning.

#### 5.2 Security-by-Design
- Backend communicates strictly via secured APIs.
- Strict CORS policies enforced.
- No direct model access from the frontend (prevents prompt injection leakage).
- LoRA adapters sandbox tasks, isolating evaluation logic from general reasoning.

#### 5.3 Model Integrity
- Base model remains separate from task-specific adapters.
- Adapters cannot override safety layers.
- All outputs validated through a post-processing filter.

#### 5.4 Transparency & Fairness
- Candidate receives explanation for every evaluation.
- Job matching includes explicit reasoning & confidence scores.
- Interview insights based on competency taxonomy, not demographic traits.
- No profiling based on sensitive or protected attributes.

### 6. Alignment with Required Criteria
| Criterion                  | How the Solution Meets It                                                                 |
|----------------------------|------------------------------------------------------------------------------------------|
| Resume Reviewer/Rewriter   | Dedicated LoRA adapter trained on structured resume data; outputs scores, corrections, and rewrite suggestions. |
| AI Interviewer & Profiler  | Specialized dialog adapter simulates recruiter behavior, extracts strengths/weaknesses, and gives interview feedback. |
| Job Matcher                | LoRA adapter trained to match JSON resumes to structured job listings and explain decisions. |
| Footprint Scanner          | Privacy-preserving analyzer for user-submitted public profile data; no unauthorized access. |
| Career Insights Report     | Multi-module pipeline that consolidates resume, job fit, interview and profile signals into a strategic growth roadmap. |
| Modular Architecture       | Adapter-based, router-driven design; scalable; easy to extend with new modules.          |
| Testing with Real/Simulated Data | Resumes, recruiter dialogs, job listings and profiles tested across scenarios.         |
| Presentation & Innovation  | Modular AI chaining + intent routing + adapter orchestration = a novel architectural approach. |
| User-centric, Privacy-by-Design | Minimal data retention, transparent outputs, strict isolation of components.          |
| Security & Professionalism | Endpoint isolation, sanitization layers, safe prompting, and consistent AI ethics compliance. |

### 7. Conclusion
The system delivers a comprehensive, secure, AI-powered career assistance solution through a highly modular architecture built around LoRA specialization and intelligent routing. Its strong privacy and security foundation, combined with multi-level AI capabilities, positions it as an innovative and scalable platform for modern job seekers.

The architecture can easily be extended with:
- Additional adapters
- Domain-specific evaluators
- Multilingual support
- More advanced scoring modules

The solution demonstrates innovation, scalability, and ethical-by-design intelligence, making it suitable for academic, industrial, or entrepreneurial deployment.

---

## Folder Structure

### `assistant-flask-api/`
- **Purpose**: Backend API for managing user requests and routing them to the appropriate AI modules.
- **Key Files**:
  - `app.py`: Main entry point for the Flask application.
  - `router.py`: Handles routing of API endpoints.
  - `model_handler.py`: Manages interactions with the AI models.
  - `requirements.txt`: Lists Python dependencies.

### `datasets/`
- **Purpose**: Contains JSONL datasets for training and testing the AI models.
- **Key Files**:
  - `job_match.jsonl`: Dataset for job matching.
  - `resume_eval.jsonl`: Dataset for resume evaluation.

### `hiring-web/`
- **Purpose**: Full-stack web application for user interaction.
- **Subfolders**:
  - `ai-hiring-backApp/`: Node.js backend for handling user authentication and CV uploads.
  - `ai-hiring-frontAPP/`: Angular frontend for user interaction.

### `flask_server/`
- **Purpose**: Additional Flask server for auxiliary tasks like LinkedIn scraping and PDF parsing.
- **Key Files**:
  - `linkedin_scrapper.py`: Scrapes LinkedIn data (with user consent).
  - `pdf_nlp_parser.py`: Parses PDF resumes for NLP processing.

### `lora_adapters/`
- **Purpose**: Contains LoRA adapters for specialized AI tasks.
- **Subfolders**:
  - `resume_eval/`: Adapter for resume evaluation.
  - `job_match/`: Adapter for job matching.
  - `recruiter_dialog/`: Adapter for recruiter simulation.
  - `latex_resume/`: Adapter for LaTeX resume generation.

### `latex_resume/`
- **Purpose**: Contains resources for generating LaTeX resumes.
- **Key Files**:
  - `adapter_config.json`: Configuration for the LaTeX resume adapter.

### `lora-train.ipynb`
- **Purpose**: Jupyter notebook for training and fine-tuning LoRA adapters.
