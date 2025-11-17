"""
Model Handler
Provides unified interfaces to run the base model, career-mode base model, and LoRA adapters.
"""
import logging
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

import torch

from model_loader import ModelLoader
from adapters import create_adapter_manager

logger = logging.getLogger(__name__)


class ModelHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.adapter_manager = None
        self.prompts = {}
        self._lock = Lock()

    def init_from_existing(self, model, tokenizer, adapter_manager, prompts_path: str = "system_prompts"):
        self.model = model
        self.tokenizer = tokenizer
        self.adapter_manager = adapter_manager
        self._load_prompts(prompts_path)
        logger.info("ModelHandler initialized from existing objects")

    def _load_prompts(self, prompts_path: str):
        p = Path(prompts_path)
        if not p.exists():
            logger.warning(f"Prompts path not found: {prompts_path}")
            return
        # Load files
        for name in ("general.txt", "career_expert.txt"):
            f = p / name
            if f.exists():
                self.prompts[name.replace('.txt','')] = f.read_text(encoding='utf-8')
            else:
                logger.warning(f"Prompt file missing: {f}")

    def _generate(self, prompt: str, max_new_tokens: int = 128, temperature: float = 0.5, do_sample: bool = False) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("ModelHandler not initialized with model/tokenizer")

        with self._lock:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature if do_sample else None,
                    top_p=0.9 if do_sample else None,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=False,
                    num_beams=1,
                )

            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return text

    def run_base_model(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        sys_prompt = self.prompts.get('general', '')
        prompt = f"{sys_prompt}\nUser: {message}\nAssistant:"
        return self._generate(prompt)

    def run_base_model_career_mode(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        sys_prompt = self.prompts.get('career_expert', '')
        prompt = f"{sys_prompt}\nUser: {message}\nAdvisor:"
        return self._generate(prompt)

    def run_with_adapter(self, adapter_name: str, prompt_text: str, max_new_tokens: int = 128) -> str:
        if self.model is None:
            raise RuntimeError("ModelHandler not initialized")

        # Load adapter (this returns a PeftModel wrapper)
        logger.info(f"ModelHandler: loading adapter {adapter_name}")
        peft_model = self.adapter_manager.load_adapter(self.model, adapter_name)

        # Generate with the adapter-wrapped model
        with self._lock:
            inputs = self.tokenizer(
                prompt_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512,
            )

            device = next(peft_model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = peft_model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=self.tokenizer.eos_token_id,
                    use_cache=False,
                    num_beams=1,
                )

            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return text


def get_model_handler() -> ModelHandler:
    return ModelHandler()
