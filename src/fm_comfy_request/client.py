from __future__ import annotations

import asyncio
import os
import random
import uuid
from pathlib import Path
from typing import Any, Callable

from fm_comfyui_bridge.lora_yaml import SdLoraYaml

from .config_lora_yaml import ConfigLoraYaml
from .exceptions import I2IUnsupportedError
from .image_io import image_bytes_to_pil, save_image
from .models import ClientSettings, GenerationResult, GeneratedImage, LoadedWorkflow
from .transport import Transport
from .workflow import (
    apply_overrides,
    build_bindings,
    build_indices,
    find_meta_node,
    insert_loras,
    list_workflows,
    load_workflow_json,
    parse_binding_yaml,
    resolve_node_reference,
    resolve_workflow_path,
    validate_i2i,
)


MAX_COMFY_SEED = 2**63 - 1


def _client_id() -> str:
    return uuid.uuid4().hex


class ComfyRequestClient:
    def __init__(self, server_url: str | None = None, workflow_dir: str | Path | None = None, timeout_seconds: float = 120.0):
        self.settings = ClientSettings(
            server_url=server_url or os.getenv("FM_COMFY_REQUEST_SERVER_URL") or "http://127.0.0.1:8188/",
            workflow_dir=Path(workflow_dir) if workflow_dir is not None else None,
            timeout_seconds=timeout_seconds,
        )
        if self.settings.workflow_dir is None:
            from .workflow import default_workflow_dir

            self.settings.workflow_dir = default_workflow_dir()

    def _load(self, workflow: str | Path) -> LoadedWorkflow:
        path = resolve_workflow_path(workflow, self.settings.workflow_dir)
        raw = load_workflow_json(path)
        node_index_by_id, node_index_by_title = build_indices(raw)
        meta_id, meta_node = find_meta_node(raw)
        parsed = parse_binding_yaml(meta_node)
        bindings = build_bindings(parsed)
        bindings.meta_node_id = meta_id
        return LoadedWorkflow(path=path, raw_workflow=raw, bindings=bindings, node_index_by_id=node_index_by_id, node_index_by_title=node_index_by_title)

    def inspect_workflow(self, workflow: str | Path) -> dict[str, Any]:
        loaded = self._load(workflow)
        return {"path": str(loaded.path), "bindings": loaded.bindings, "nodes": list(loaded.raw_workflow.keys())}

    def list_workflows(self) -> list[Path]:
        return list_workflows(workflow_dir=self.settings.workflow_dir)

    def free(self, server_url: str | None = None):
        return Transport(server_url or self.settings.server_url, timeout=self.settings.timeout_seconds).free()

    def list_models(self, folder: str, server_url: str | None = None):
        return Transport(server_url or self.settings.server_url, timeout=self.settings.timeout_seconds).list_models(folder)

    def _lora_cfg(self, lora: SdLoraYaml | ConfigLoraYaml | None) -> ConfigLoraYaml | None:
        if lora is None:
            return None
        if isinstance(lora, ConfigLoraYaml):
            return lora
        return ConfigLoraYaml(data=dict(getattr(lora, "data", {})), recent_file=getattr(lora, "recent_file", None))

    def _model_name(self, lora: ConfigLoraYaml | None) -> str | None:
        if lora is None:
            return None
        model = lora.data.get("model", lora.data.get("checkpoint"))
        return str(model) if model is not None else None

    def _run(
        self,
        workflow: str | Path,
        model: str | None = None,
        prompt: str | None = None,
        negative: str | None = None,
        lora: SdLoraYaml | ConfigLoraYaml | None = None,
        seed: int | None = None,
        random_seed: bool = True,
        denoise: float | None = None,
        server_url: str | None = None,
        input_image: str | bytes | None = None,
        i2i: bool = False,
        progress_callback: Callable | None = None,
    ) -> GenerationResult:
        loaded = self._load(workflow)
        if i2i:
            validate_i2i(loaded)
        if seed is None and random_seed and loaded.bindings.seed:
            seed = random.randint(0, MAX_COMFY_SEED)
        lora_cfg = self._lora_cfg(lora)
        final_workflow = apply_overrides(
            loaded,
            model=model or self._model_name(lora_cfg),
            prompt=prompt,
            negative=negative,
            seed=seed,
            denoise=denoise,
        )
        final_workflow = insert_loras(loaded, final_workflow, lora_cfg)
        transport = Transport(server_url or self.settings.server_url, timeout=self.settings.timeout_seconds)
        if i2i and input_image is not None:
            upload_name = f"fm_comfy_request_{_client_id()}.png"
            if isinstance(input_image, (str, Path)):
                image_bytes = Path(input_image).read_bytes()
                upload_name = Path(input_image).name
            else:
                image_bytes = bytes(input_image)
            transport.upload_image(upload_name, image_bytes)
            final_workflow[resolve_node_reference(final_workflow, loaded.node_index_by_title, loaded.bindings.input)]["inputs"]["image"] = upload_name
        client_id = _client_id()
        prompt_id = transport.submit_prompt(final_workflow, client_id)
        transport.watch(client_id, prompt_id, callback=progress_callback)
        history = transport.history(prompt_id)
        history_entry = history.get(prompt_id, history if isinstance(history, dict) else {})
        outputs = history_entry.get("outputs", {}) if isinstance(history_entry, dict) else {}
        images: list[GeneratedImage] = []
        output_node_id = resolve_node_reference(final_workflow, loaded.node_index_by_title, loaded.bindings.output) if loaded.bindings.output else None
        if output_node_id and output_node_id in outputs:
            for image in outputs[output_node_id].get("images", []):
                image_bytes = transport.view(image["subfolder"], image["filename"])
                images.append(GeneratedImage(filename=image["filename"], subfolder=image["subfolder"], type=image.get("type", "output"), image_bytes=image_bytes))
        return GenerationResult(prompt_id=prompt_id, client_id=client_id, workflow_path=loaded.path, workflow_final=final_workflow, output_node_id=output_node_id, images=images, history=history)

    def generate(self, workflow: str | Path, prompt: str | None = None, negative: str | None = None, lora: SdLoraYaml | ConfigLoraYaml | None = None, model: str | None = None, seed: int | None = None, random_seed: bool = True, denoise: float | None = None, server_url: str | None = None, progress_callback: Callable | None = None):
        return self._run(workflow, model=model, prompt=prompt, negative=negative, lora=lora, seed=seed, random_seed=random_seed, denoise=denoise, server_url=server_url, progress_callback=progress_callback)

    def generate_i2i(self, workflow: str | Path, input_image: str | bytes, prompt: str | None = None, negative: str | None = None, lora: SdLoraYaml | ConfigLoraYaml | None = None, model: str | None = None, seed: int | None = None, random_seed: bool = True, denoise: float | None = None, server_url: str | None = None, progress_callback: Callable | None = None):
        return self._run(workflow, model=model, prompt=prompt, negative=negative, lora=lora, seed=seed, random_seed=random_seed, denoise=denoise, server_url=server_url, input_image=input_image, i2i=True, progress_callback=progress_callback)


class AsyncComfyRequestClient(ComfyRequestClient):
    async def generate_async(self, *args, **kwargs):
        return await asyncio.to_thread(self.generate, *args, **kwargs)

    async def generate_i2i_async(self, *args, **kwargs):
        return await asyncio.to_thread(self.generate_i2i, *args, **kwargs)
