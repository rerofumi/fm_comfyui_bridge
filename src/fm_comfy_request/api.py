from __future__ import annotations

from pathlib import Path
from typing import Callable

from fm_comfyui_bridge.lora_yaml import SdLoraYaml

from .client import AsyncComfyRequestClient, ComfyRequestClient
from .image_io import image_bytes_to_pil, save_image
from .workflow import list_workflows as _list_workflows


def _client(server_url: str | None = None, workflow_dir: str | Path | None = None):
    return ComfyRequestClient(server_url=server_url, workflow_dir=workflow_dir)


def generate(workflow: str | Path, *, model: str | None = None, prompt: str | None = None, negative: str | None = None, lora: SdLoraYaml | None = None, seed: int | None = None, random_seed: bool = True, server_url: str | None = None, workflow_dir: str | Path | None = None, progress_callback: Callable | None = None):
    return _client(server_url, workflow_dir).generate(workflow, model=model, prompt=prompt, negative=negative, lora=lora, seed=seed, random_seed=random_seed, server_url=server_url, progress_callback=progress_callback)


async def generate_async(workflow: str | Path, *, model: str | None = None, prompt: str | None = None, negative: str | None = None, lora: SdLoraYaml | None = None, seed: int | None = None, random_seed: bool = True, server_url: str | None = None, workflow_dir: str | Path | None = None, progress_callback: Callable | None = None):
    return await AsyncComfyRequestClient(server_url=server_url, workflow_dir=workflow_dir).generate_async(workflow, model=model, prompt=prompt, negative=negative, lora=lora, seed=seed, random_seed=random_seed, server_url=server_url, progress_callback=progress_callback)


def generate_i2i(workflow: str | Path, input_image: str | bytes, *, model: str | None = None, prompt: str | None = None, negative: str | None = None, lora: SdLoraYaml | None = None, seed: int | None = None, random_seed: bool = True, server_url: str | None = None, workflow_dir: str | Path | None = None, progress_callback: Callable | None = None):
    return _client(server_url, workflow_dir).generate_i2i(workflow, input_image, model=model, prompt=prompt, negative=negative, lora=lora, seed=seed, random_seed=random_seed, server_url=server_url, progress_callback=progress_callback)


async def generate_i2i_async(workflow: str | Path, input_image: str | bytes, *, model: str | None = None, prompt: str | None = None, negative: str | None = None, lora: SdLoraYaml | None = None, seed: int | None = None, random_seed: bool = True, server_url: str | None = None, workflow_dir: str | Path | None = None, progress_callback: Callable | None = None):
    return await AsyncComfyRequestClient(server_url=server_url, workflow_dir=workflow_dir).generate_i2i_async(workflow, input_image, model=model, prompt=prompt, negative=negative, lora=lora, seed=seed, random_seed=random_seed, server_url=server_url, progress_callback=progress_callback)


def list_models(folder: str, *, server_url: str | None = None, workflow_dir: str | Path | None = None):
    return _client(server_url, workflow_dir).list_models(folder, server_url=server_url)


def free(*, server_url: str | None = None, workflow_dir: str | Path | None = None):
    return _client(server_url, workflow_dir).free(server_url=server_url)


def inspect_workflow(workflow: str | Path, *, workflow_dir: str | Path | None = None):
    return _client(None, workflow_dir).inspect_workflow(workflow)


def list_workflows(*, workflow_dir: str | Path | None = None):
    return [str(path) for path in _list_workflows(workflow_dir=workflow_dir)]
