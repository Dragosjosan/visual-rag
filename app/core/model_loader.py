from typing import Optional

import torch
from colpali_engine.models import ColQwen2, ColQwen2Processor
from loguru import logger

from app.core.config import settings


def _get_device(preferred_device: str) -> torch.device:
    if preferred_device == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    elif preferred_device == "mps" and torch.backends.mps.is_available():
        return torch.device("mps")
    elif preferred_device == "cpu":
        return torch.device("cpu")
    else:
        if torch.cuda.is_available():
            logger.info(f"Preferred device '{preferred_device}' not available, using CUDA")
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            logger.info(f"Preferred device '{preferred_device}' not available, using MPS")
            return torch.device("mps")
        else:
            logger.warning("No GPU detected, falling back to CPU")
            return torch.device("cpu")


class ColQwen2ModelLoader:
    _instance: Optional["ColQwen2ModelLoader"] = None
    _model: Optional[ColQwen2] = None
    _processor: Optional[ColQwen2Processor] = None

    def __new__(cls) -> "ColQwen2ModelLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self) -> None:
        if self._model is not None:
            return

        logger.info(f"Loading ColQwen2 model: {settings.colqwen2_model_name}")

        device = _get_device(settings.colqwen2_device)
        logger.info(f"Using device: {device}")

        if device.type in ["mps", "cpu"]:
            self._model = ColQwen2.from_pretrained(
                settings.colqwen2_model_name,
                dtype=torch.bfloat16,
            ).to(device).eval()
        else:
            self._model = ColQwen2.from_pretrained(
                settings.colqwen2_model_name,
                dtype=torch.bfloat16,
                device_map=device.type,
            ).eval()

        self._processor = ColQwen2Processor.from_pretrained(settings.colqwen2_model_name)

        logger.success(f"Model loaded successfully on {device}")

    @property
    def model(self) -> ColQwen2:
        if self._model is None:
            self._load_model()
        return self._model

    @property
    def processor(self) -> ColQwen2Processor:
        if self._processor is None:
            self._load_model()
        return self._processor

    def is_loaded(self) -> bool:
        return self._model is not None


def get_model_loader() -> ColQwen2ModelLoader:
    return ColQwen2ModelLoader()
