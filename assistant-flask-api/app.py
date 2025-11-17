"""
Flask API Application
Serves Phi-3 model with dynamic LoRA adapter loading.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any
from threading import Lock
import json

import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

from model_loader import ModelLoader, load_model_and_tokenizer
from adapters import create_adapter_manager
from router import AssistantRouter
from model_handler import get_model_handler, ModelHandler


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global state
model = None
tokenizer = None
adapter_manager = None
inference_lock = Lock()
model_handler = None
router = None

# Configuration
BASE_MODEL_PATH = os.getenv(
    "BASE_MODEL_PATH",
    "../Phi-3-mini-4k-instruct"
)
ADAPTERS_BASE_PATH = os.getenv(
    "ADAPTERS_BASE_PATH",
    "../lora_adapters"
)
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))


class InferenceConfig:
    """Configuration for inference."""
    max_new_tokens: int = 128  # Reduced from 512 for faster inference
    temperature: float = 0.5  # Reduced from 0.7 for deterministic output
    top_p: float = 0.9  # Reduced from 0.95
    do_sample: bool = False  # Use greedy decoding for speed


def initialize_model():
    """Initialize the base model and adapter manager at startup."""
    global model, tokenizer, adapter_manager
    global model_handler, router
    
    try:
        logger.info("Initializing model and adapters...")
        
        # Validate paths exist
        model_path = Path(BASE_MODEL_PATH)
        adapters_path = Path(ADAPTERS_BASE_PATH)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model path not found: {BASE_MODEL_PATH}")
        if not adapters_path.exists():
            raise FileNotFoundError(f"Adapters path not found: {ADAPTERS_BASE_PATH}")
        
        # Load base model and tokenizer
        logger.info(f"Loading model from {BASE_MODEL_PATH}")
        model, tokenizer = load_model_and_tokenizer(str(model_path))
        logger.info("Model loaded successfully")
        
        # Initialize adapter manager
        adapter_manager = create_adapter_manager(str(adapters_path))
        available_adapters = adapter_manager.list_available_adapters()
        logger.info(f"Available adapters: {available_adapters}")
        
        # Initialize model handler and router
        model_handler = get_model_handler()
        model_handler.init_from_existing(model, tokenizer, adapter_manager)
        router = AssistantRouter()
        logger.info("Model handler and router initialized")
        
        logger.info("Initialization complete!")
        
    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        raise


def generate_response(prompt: str, adapter_name: str = None) -> str:
    """
    Generate a response using the model with optional adapter.
    
    Args:
        prompt: Input prompt
        adapter_name: Optional adapter name to load
    
    Returns:
        Generated text
    
    Raises:
        RuntimeError: If generation fails
    """
    global model, tokenizer, adapter_manager
    
    with inference_lock:
        try:
            # Delegate to model_handler when available
            if model_handler is None:
                raise RuntimeError("Model handler not ready")

            if adapter_name:
                return model_handler.run_with_adapter(adapter_name, prompt, max_new_tokens=InferenceConfig.max_new_tokens)
            else:
                return model_handler._generate(prompt, max_new_tokens=InferenceConfig.max_new_tokens, temperature=InferenceConfig.temperature, do_sample=InferenceConfig.do_sample)
        
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise RuntimeError(f"Text generation failed: {str(e)}") from e


# ==================== API ENDPOINTS ====================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "adapters_ready": adapter_manager is not None,
    }), 200


@app.route("/adapters", methods=["GET"])
def list_adapters():
    """List all available adapters."""
    try:
        if adapter_manager is None:
            return jsonify({"error": "Adapter manager not initialized"}), 503
        
        adapters = adapter_manager.list_available_adapters()
        return jsonify({
            "available_adapters": adapters,
            "count": len(adapters),
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to list adapters: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/run/job_match", methods=["POST"])
def job_match():
    """
    Run job matching inference.
    
    Expects JSON:
    {
        "resume_json": {...},
        "job_offers_json": [...]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume_json = data.get("resume_json")
        job_offers_json = data.get("job_offers_json")
        
        if resume_json is None or job_offers_json is None:
            return jsonify({
                "error": "Missing required fields: resume_json, job_offers_json"
            }), 400
        
        # Create prompt
        prompt = f"""Based on the following resume and job offers, provide a job matching analysis:

Resume:
{json.dumps(resume_json, indent=2)}

Job Offers:
{json.dumps(job_offers_json, indent=2)}

Analysis:"""
        
        # Generate response
        response = generate_response(prompt, adapter_name="job_match")
        
        return jsonify({
            "adapter": "job_match",
            "response": response,
            "status": "success",
        }), 200
    
    except Exception as e:
        logger.error(f"job_match endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/run/resume_eval", methods=["POST"])
def resume_eval():
    """
    Run resume evaluation inference.
    
    Expects JSON:
    {
        "resume_json": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume_json = data.get("resume_json")
        
        if resume_json is None:
            return jsonify({"error": "Missing required field: resume_json"}), 400
        
        # Create prompt
        prompt = f"""Please evaluate the following resume and provide constructive feedback:

Resume:
{json.dumps(resume_json, indent=2)}

Evaluation:"""
        
        # Generate response
        response = generate_response(prompt, adapter_name="resume_eval")
        
        return jsonify({
            "adapter": "resume_eval",
            "response": response,
            "status": "success",
        }), 200
    
    except Exception as e:
        logger.error(f"resume_eval endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/run/latex_resume", methods=["POST"])
def latex_resume():
    """
    Generate LaTeX resume format.
    
    Expects JSON:
    {
        "resume_json": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        resume_json = data.get("resume_json")
        
        if resume_json is None:
            return jsonify({"error": "Missing required field: resume_json"}), 400
        
        # Create prompt
        prompt = f"""Convert the following resume data into a well-formatted LaTeX resume:

Resume Data:
{json.dumps(resume_json, indent=2)}

LaTeX Resume:"""
        
        # Generate response
        response = generate_response(prompt, adapter_name="latex_resume")
        
        return jsonify({
            "adapter": "latex_resume",
            "response": response,
            "status": "success",
        }), 200
    
    except Exception as e:
        logger.error(f"latex_resume endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/run/recruiter_dialog", methods=["POST"])
def recruiter_dialog():
    """
    Run recruiter dialog inference.
    
    Expects JSON:
    {
        "message": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        message = data.get("message")
        
        if not message or not isinstance(message, str):
            return jsonify({"error": "Missing or invalid required field: message"}), 400
        
        # Create prompt
        prompt = f"""You are a professional recruiter. Respond to the following message:

Message: {message}

Response:"""
        
        # Generate response
        response = generate_response(prompt, adapter_name="recruiter_dialog")
        
        return jsonify({
            "adapter": "recruiter_dialog",
            "response": response,
            "status": "success",
        }), 200
    
    except Exception as e:
        logger.error(f"recruiter_dialog endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.route("/assistant", methods=["POST"])
def assistant():
    """
    Unified assistant endpoint. Body:
    {
      "message": "string",
      "context": {},
      "resume_json": {},
      "job_offers_json": []
    }
    """
    try:
        body = request.get_json() or {}

        if router is None or model_handler is None:
            return jsonify({"error": "Server not fully initialized"}), 503

        mode, normalized = router.detect_intent(body)

        message = normalized.get("message", "")
        resume = normalized.get("resume_json")
        offers = normalized.get("job_offers_json")

        # Route to appropriate handler
        if mode == "general":
            resp = model_handler.run_base_model(message, normalized.get("context"))
        elif mode == "career":
            resp = model_handler.run_base_model_career_mode(message, normalized.get("context"))
        elif mode == "resume_eval":
            prompt = f"Please evaluate the following resume:\n\n{json.dumps(resume, indent=2)}\n\nEvaluation:"
            resp = model_handler.run_with_adapter("resume_eval", prompt, max_new_tokens=128)
        elif mode == "job_match":
            prompt = f"Based on the resume and job offers below, provide a matching analysis:\n\nResume:\n{json.dumps(resume, indent=2)}\n\nJob Offers:\n{json.dumps(offers, indent=2)}\n\nAnalysis:"
            resp = model_handler.run_with_adapter("job_match", prompt, max_new_tokens=128)
        elif mode == "recruiter":
            prompt = f"You are a professional recruiter. Respond to the following message:\n\nMessage: {message}\n\nResponse:" 
            resp = model_handler.run_with_adapter("recruiter_dialog", prompt, max_new_tokens=128)
        elif mode == "latex_resume":
            prompt = f"Convert the following resume to LaTeX:\n\n{json.dumps(resume, indent=2)}\n\nLaTeX:" 
            resp = model_handler.run_with_adapter("latex_resume", prompt, max_new_tokens=256)
        else:
            resp = model_handler.run_base_model(message, normalized.get("context"))

        return jsonify({
            "mode": mode,
            "response": resp,
        }), 200

    except Exception as e:
        logger.error(f"assistant endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


# ==================== STARTUP ====================

@app.before_request
def before_request():
    """Check that model is initialized before each request."""
    if model is None or adapter_manager is None:
        return jsonify({
            "error": "Model not initialized. Please try again in a moment."
        }), 503


if __name__ == "__main__":
    try:
        # Initialize model on startup
        initialize_model()
        
        # Run Flask app
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            threaded=True,
        )
    
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        raise
