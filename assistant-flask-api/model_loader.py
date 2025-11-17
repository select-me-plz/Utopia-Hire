"""
Model Loader Module
Handles loading the base Phi-3 model with 4-bit quantization.
"""

import os
import logging
from pathlib import Path
from typing import Tuple

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
)

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton-like class to manage model and tokenizer loading."""
    
    _instance = None
    _model = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    @staticmethod
    def load_base_model(model_path: str) -> Tuple:
        """
        Load the base Phi-3 model with CPU-friendly settings.
        
        Args:
            model_path: Path to the model directory (e.g., ./Phi-3-mini-4k-instruct/)
        
        Returns:
            Tuple of (model, tokenizer)
        
        Raises:
            FileNotFoundError: If model path does not exist
            RuntimeError: If model loading fails
        """
        
        # Validate model path exists
        model_dir = Path(model_path)
        if not model_dir.exists():
            raise FileNotFoundError(f"Model path does not exist: {model_path}")
        
        logger.info(f"Loading base model from {model_path}")
        
        try:
            logger.info("Loading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=True,
            )
            logger.info("Tokenizer loaded successfully")
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Load model with device mapping
            logger.info("Loading model...")
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto" if device == "cuda" else None,
                dtype=torch.float16 if device == "cuda" else torch.float32,
                local_files_only=True,
                trust_remote_code=True,
            )
            
            # Move to device if CPU
            if device == "cpu":
                model = model.to(device)
            
            logger.info("Model loaded successfully")
            
            # Set model to eval mode
            model.eval()
            
            return model, tokenizer
        
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model loading failed: {str(e)}") from e
    
    @classmethod
    def get_model_and_tokenizer(cls, model_path: str) -> Tuple:
        """
        Get or create model and tokenizer (lazy loading).
        
        Args:
            model_path: Path to the model directory
        
        Returns:
            Tuple of (model, tokenizer)
        """
        
        if cls._model is None or cls._tokenizer is None:
            cls._model, cls._tokenizer = cls.load_base_model(model_path)
        
        return cls._model, cls._tokenizer
    
    @classmethod
    def get_model(cls):
        """Get the loaded model."""
        if cls._model is None:
            raise RuntimeError("Model not loaded. Call get_model_and_tokenizer() first.")
        return cls._model
    
    @classmethod
    def get_tokenizer(cls):
        """Get the loaded tokenizer."""
        if cls._tokenizer is None:
            raise RuntimeError("Tokenizer not loaded. Call get_model_and_tokenizer() first.")
        return cls._tokenizer
    
    @classmethod
    def unload(cls):
        """Unload model and tokenizer (free memory)."""
        cls._model = None
        cls._tokenizer = None
        logger.info("Model and tokenizer unloaded")


def load_model_and_tokenizer(model_path: str) -> Tuple:
    """
    Convenience function to load the base model and tokenizer.
    
    Args:
        model_path: Path to the model directory
    
    Returns:
        Tuple of (model, tokenizer)
    """
    loader = ModelLoader()
    return loader.get_model_and_tokenizer(model_path)
