"""
Adapters Module
Handles dynamic loading and management of LoRA adapters.
"""

import logging
from pathlib import Path
from typing import Optional
from threading import Lock

from peft import PeftModel, LoraConfig
from transformers import PreTrainedModel

logger = logging.getLogger(__name__)


class AdapterManager:
    """
    Manages LoRA adapter loading and switching.
    Uses thread-safe operations for concurrent access.
    """
    
    def __init__(self, adapters_base_path: str):
        """
        Initialize the adapter manager.
        
        Args:
            adapters_base_path: Base path where all adapters are stored
                               (e.g., ./lora_adapters/)
        """
        self.adapters_base_path = Path(adapters_base_path)
        self._current_adapter = None
        self._lock = Lock()
        
        # Validate adapters path exists
        if not self.adapters_base_path.exists():
            raise FileNotFoundError(
                f"Adapters base path does not exist: {adapters_base_path}"
            )
        
        logger.info(f"AdapterManager initialized with base path: {adapters_base_path}")
    
    def get_adapter_path(self, adapter_name: str) -> Path:
        """
        Get the full path to an adapter directory.
        
        Args:
            adapter_name: Name of the adapter (e.g., 'job_match')
        
        Returns:
            Path object pointing to adapter directory
        
        Raises:
            FileNotFoundError: If adapter directory doesn't exist
        """
        adapter_path = self.adapters_base_path / adapter_name
        
        if not adapter_path.exists():
            raise FileNotFoundError(
                f"Adapter '{adapter_name}' not found at {adapter_path}"
            )
        
        # Check for adapter_model.safetensors
        adapter_model_file = adapter_path / "adapter_model.safetensors"
        if not adapter_model_file.exists():
            raise FileNotFoundError(
                f"adapter_model.safetensors not found in {adapter_path}"
            )
        
        return adapter_path
    
    def load_adapter(
        self, 
        model: PreTrainedModel, 
        adapter_name: str
    ) -> PreTrainedModel:
        """
        Load a LoRA adapter and apply it to the model.
        Thread-safe operation.
        
        Args:
            model: The base model to apply the adapter to
            adapter_name: Name of the adapter (e.g., 'job_match')
        
        Returns:
            Model with the adapter applied (wrapped in PeftModel)
        
        Raises:
            FileNotFoundError: If adapter doesn't exist
            RuntimeError: If adapter loading fails
        """
        with self._lock:
            try:
                adapter_path = self.get_adapter_path(adapter_name)
                logger.info(f"Loading adapter '{adapter_name}' from {adapter_path}")
                
                # Check if the model already has a PEFT config
                # If so, we need to merge and reload
                if hasattr(model, 'peft_config') and model.peft_config:
                    logger.info("Merging existing adapter and reloading new one")
                    # Merge existing adapter weights into base model
                    if hasattr(model, 'merge_and_unload'):
                        model = model.merge_and_unload()
                
                # Load the new adapter
                model = PeftModel.from_pretrained(
                    model,
                    str(adapter_path),
                    device_map="auto",
                    torch_dtype="auto",
                )
                
                model.eval()
                self._current_adapter = adapter_name
                logger.info(f"Adapter '{adapter_name}' loaded successfully")
                
                return model
            
            except Exception as e:
                logger.error(f"Failed to load adapter '{adapter_name}': {str(e)}")
                raise RuntimeError(
                    f"Adapter loading failed for '{adapter_name}': {str(e)}"
                ) from e
    
    def get_current_adapter(self) -> Optional[str]:
        """
        Get the name of the currently loaded adapter.
        
        Returns:
            Adapter name or None if no adapter is loaded
        """
        return self._current_adapter
    
    def list_available_adapters(self) -> list:
        """
        List all available adapters in the base path.
        
        Returns:
            List of adapter names (directory names)
        """
        adapters = []
        for item in self.adapters_base_path.iterdir():
            if item.is_dir():
                adapter_model_file = item / "adapter_model.safetensors"
                if adapter_model_file.exists():
                    adapters.append(item.name)
        
        return sorted(adapters)


def create_adapter_manager(adapters_base_path: str) -> AdapterManager:
    """
    Convenience function to create an adapter manager.
    
    Args:
        adapters_base_path: Base path where all adapters are stored
    
    Returns:
        AdapterManager instance
    """
    return AdapterManager(adapters_base_path)
