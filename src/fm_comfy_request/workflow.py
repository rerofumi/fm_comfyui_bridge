from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any

import yaml

from .config_lora_yaml import ConfigLoraYaml
from .exceptions import (
    I2IUnsupportedError,
    LoraClipOutputMissingError,
    NodeReferenceAmbiguousError,
    NodeReferenceNotFoundError,
    WorkflowLoadError,
    WorkflowMetaConflictError,
    WorkflowMetaInvalidError,
    WorkflowMetaNotFoundError,
    WorkflowNotFoundError,
    WorkflowValidationError,
)
from .models import LoadedWorkflow, WorkflowBindingSet


def default_workflow_dir() -> Path:
    env = os.getenv("FM_COMFY_REQUEST_WORKFLOW_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config" / "fm_comfy_request" / "workflow"


def resolve_workflow_path(
    workflow: str | Path, workflow_dir: Path | None = None
) -> Path:
    path = Path(workflow)
    if path.is_absolute():
        if path.exists():
            return path
        raise WorkflowNotFoundError(f"workflow not found: {path}")
    workflow_dir = workflow_dir or default_workflow_dir()
    candidates = [workflow_dir / path]
    if path.suffix != ".json":
        candidates.append(workflow_dir / f"{path}.json")
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise WorkflowNotFoundError(f"workflow not found: {workflow} (dir={workflow_dir})")


def load_workflow_json(path: str | Path) -> dict[str, Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError as exc:
        raise WorkflowNotFoundError(f"workflow not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkflowLoadError(f"invalid workflow json: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise WorkflowLoadError(f"workflow must be an object: {path}")
    return data


def list_workflows(workflow_dir: Path | None = None) -> list[Path]:
    workflow_dir = workflow_dir or default_workflow_dir()
    if not workflow_dir.exists():
        return []
    return sorted(
        p for p in workflow_dir.iterdir() if p.is_file() and p.suffix == ".json"
    )


def _meta_title(node: dict[str, Any]) -> str | None:
    meta = node.get("_meta") or {}
    if isinstance(meta, dict) and meta.get("title"):
        return str(meta["title"])
    title = node.get("title")
    return str(title) if title is not None else None


def find_meta_node(workflow: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    matches = [
        (node_id, node)
        for node_id, node in workflow.items()
        if _meta_title(node) == "fm_comfy_request"
    ]
    if not matches:
        raise WorkflowMetaNotFoundError("fm_comfy_request meta node not found")
    if len(matches) > 1:
        raise WorkflowMetaConflictError("multiple fm_comfy_request meta nodes found")
    return matches[0]


def _get_meta_text(node: dict[str, Any]) -> str:
    inputs = node.get("inputs") or {}
    for key in ("text", "value", "string"):
        value = inputs.get(key)
        if isinstance(value, str):
            return value
    raise WorkflowMetaInvalidError("meta node has no yaml text input")


def parse_binding_yaml(node: dict[str, Any]) -> dict[str, Any]:
    raw = _get_meta_text(node)
    try:
        parsed = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        raise WorkflowMetaInvalidError(f"invalid binding yaml: {exc}") from exc
    if not isinstance(parsed, dict):
        raise WorkflowMetaInvalidError("binding yaml must be a mapping")
    normalized: dict[str, Any] = {}
    for key, value in parsed.items():
        if key == "negative_prompt":
            key = "negative-prompt"
        elif key == "samplingーmode":
            key = "sampling-mode"
        normalized[key] = value
    return normalized


def build_bindings(parsed: dict[str, Any]) -> WorkflowBindingSet:
    model = parsed.get("model")
    if not model:
        raise WorkflowMetaInvalidError("binding yaml requires model")
    return WorkflowBindingSet(
        meta_node_id="",
        model=str(model),
        clip=str(parsed["clip"]) if parsed.get("clip") is not None else None,
        prompt=str(parsed["prompt"]) if parsed.get("prompt") is not None else None,
        negative_prompt=str(parsed["negative-prompt"])
        if parsed.get("negative-prompt") is not None
        else None,
        seed=str(parsed["seed"]) if parsed.get("seed") is not None else None,
        output=str(parsed["output"]) if parsed.get("output") is not None else None,
        input=str(parsed["input"]) if parsed.get("input") is not None else None,
        size=str(parsed["size"]) if parsed.get("size") is not None else None,
        size_width=str(parsed["size-width"])
        if parsed.get("size-width") is not None
        else None,
        size_height=str(parsed["size-height"])
        if parsed.get("size-height") is not None
        else None,
        sampling_mode=str(parsed["sampling-mode"])
        if parsed.get("sampling-mode") is not None
        else None,
        steps=str(parsed["steps"]) if parsed.get("steps") is not None else None,
        cfg=str(parsed["cfg"]) if parsed.get("cfg") is not None else None,
        denoise=str(parsed["denoise"])
        if parsed.get("denoise") is not None
        else None,
        seed_name=str(parsed.get("seed-name", "noise_seed")),
    )


def build_indices(
    workflow: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[str]]]:
    by_id = {node_id: node for node_id, node in workflow.items()}
    by_title: dict[str, list[str]] = {}
    for node_id, node in workflow.items():
        title = _meta_title(node)
        if title:
            by_title.setdefault(title, []).append(node_id)
    return by_id, by_title


def resolve_node_reference(
    workflow: dict[str, Any], node_index_by_title: dict[str, list[str]], ref: str
) -> str:
    if ref in workflow:
        return ref
    matches = node_index_by_title.get(ref, [])
    if not matches:
        raise NodeReferenceNotFoundError(f"node not found: {ref}")
    if len(matches) > 1:
        raise NodeReferenceAmbiguousError(f"node title is ambiguous: {ref}")
    return matches[0]


def _output_slot(node: dict[str, Any], kind: str) -> int | None:
    class_type = node.get("class_type")
    if kind == "model":
        return 0
    if kind == "clip":
        if class_type in {"CheckpointLoaderSimple", "LoraLoader"}:
            return 1
        if class_type == "CLIPLoader":
            return 0
    return None


def _replace_links(
    value: Any,
    old_id: str,
    new_id: str,
    old_slot: int | None = None,
    new_slot: int | None = None,
) -> Any:
    if (
        isinstance(value, list)
        and len(value) == 2
        and value[0] == old_id
        and isinstance(value[1], int)
    ):
        if old_slot is not None and value[1] != old_slot:
            return value
        slot = new_slot if new_slot is not None else value[1]
        return [new_id, slot]
    if isinstance(value, list):
        return [
            _replace_links(item, old_id, new_id, old_slot, new_slot) for item in value
        ]
    if isinstance(value, dict):
        return {
            key: _replace_links(item, old_id, new_id, old_slot, new_slot)
            for key, item in value.items()
        }
    return value


def _model_input_name(node: dict[str, Any]) -> str | None:
    class_type = node.get("class_type")
    if class_type == "CheckpointLoaderSimple":
        return "ckpt_name"
    if class_type == "UNETLoader":
        return "unet_name"
    return None


def apply_overrides(
    loaded: LoadedWorkflow,
    model: str | None = None,
    prompt: str | None = None,
    negative: str | None = None,
    seed: int | None = None,
    width: int | None = None,
    height: int | None = None,
    steps: int | None = None,
    cfg: float | None = None,
    denoise: float | None = None,
    sampling_mode: str | None = None,
) -> dict[str, Any]:
    workflow = copy.deepcopy(loaded.raw_workflow)
    b = loaded.bindings
    if model is not None:
        node = workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.model)
        ]
        input_name = _model_input_name(node)
        if input_name is None:
            raise WorkflowValidationError(
                f"model input not found for {b.model}: {node.get('class_type')}"
            )
        node.setdefault("inputs", {})[input_name] = model
    if prompt is not None and b.prompt:
        workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.prompt)
        ]["inputs"]["text"] = prompt
    if negative is not None and b.negative_prompt:
        workflow[
            resolve_node_reference(
                workflow, loaded.node_index_by_title, b.negative_prompt
            )
        ]["inputs"]["text"] = negative
    if seed is not None and b.seed:
        node = workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.seed)
        ]
        inputs = node.setdefault("inputs", {})
        seed_name = b.seed_name
        if seed_name not in inputs and seed_name == "noise_seed" and "seed" in inputs:
            seed_name = "seed"
        inputs[seed_name] = seed
    if width is not None and b.size_width:
        workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.size_width)
        ]["inputs"]["value"] = width
    if height is not None and b.size_height:
        workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.size_height)
        ]["inputs"]["value"] = height
    if width is not None and height is not None and b.size:
        node = workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.size)
        ]
        node.setdefault("inputs", {})["width"] = width
        node.setdefault("inputs", {})["height"] = height
    if steps is not None and b.steps:
        workflow[resolve_node_reference(workflow, loaded.node_index_by_title, b.steps)][
            "inputs"
        ]["steps"] = steps
    if cfg is not None and b.cfg:
        workflow[resolve_node_reference(workflow, loaded.node_index_by_title, b.cfg)][
            "inputs"
        ]["cfg"] = cfg
    if denoise is not None and b.denoise:
        workflow[
            resolve_node_reference(workflow, loaded.node_index_by_title, b.denoise)
        ]["inputs"]["denoise"] = denoise
    if sampling_mode is not None and b.sampling_mode:
        workflow[
            resolve_node_reference(
                workflow, loaded.node_index_by_title, b.sampling_mode
            )
        ]["inputs"]["sampling"] = sampling_mode
    return workflow


def insert_loras(
    loaded: LoadedWorkflow, workflow: dict[str, Any], lora: ConfigLoraYaml | None
) -> dict[str, Any]:
    if lora is None or lora.lora_num == 0:
        return workflow
    bindings = loaded.bindings
    model_id = resolve_node_reference(
        workflow, loaded.node_index_by_title, bindings.model
    )
    model_node = workflow[model_id]
    current_model = [model_id, _output_slot(model_node, "model")]
    if current_model[1] is None:
        raise WorkflowValidationError(f"model output not found for {bindings.model}")
    current_clip = None
    if bindings.clip:
        clip_id = resolve_node_reference(
            workflow, loaded.node_index_by_title, bindings.clip
        )
        clip_slot = _output_slot(workflow[clip_id], "clip")
        if clip_slot is None:
            raise LoraClipOutputMissingError(
                f"clip output not found for {bindings.clip}"
            )
        current_clip = [clip_id, clip_slot]
    else:
        clip_slot = _output_slot(model_node, "clip")
        if clip_slot is not None:
            current_clip = [model_id, clip_slot]
    used: set[str] = set()
    for index in range(lora.lora_num):
        if not lora.lora_enabled_flag(index):
            continue
        model_only = bool(
            getattr(lora, "lora_model_only", lambda _i=index: False)(index)
        )
        new_id = str(
            max([int(node_id) for node_id in workflow if str(node_id).isdigit()] + [0])
            + 1
        )
        while new_id in workflow or new_id in used:
            new_id = str(int(new_id) + 1)
        used.add(new_id)
        node = {
            "inputs": {
                "lora_name": lora.lora_model(index),
                "strength_model": lora.lora_strength(index),
                "strength_clip": lora.lora_strength(index),
                "model": current_model,
            },
            "class_type": "LoraLoaderModelOnly" if model_only else "LoraLoader",
            "_meta": {"title": "fm_comfy_request_lora"},
        }
        if not model_only:
            if current_clip is None:
                raise LoraClipOutputMissingError(
                    "clip output is required for clip-attached lora"
                )
            node["inputs"]["clip"] = current_clip
        old_model_id = current_model[0]
        old_model_slot = current_model[1]
        old_clip_id = current_clip[0] if current_clip is not None else None
        old_clip_slot = current_clip[1] if current_clip is not None else None
        workflow[new_id] = node
        for other_id in list(workflow.keys()):
            if other_id == new_id:
                continue
            workflow[other_id] = _replace_links(
                workflow[other_id],
                old_model_id,
                new_id,
                old_slot=old_model_slot,
                new_slot=0,
            )
            if old_clip_id is not None:
                workflow[other_id] = _replace_links(
                    workflow[other_id],
                    old_clip_id,
                    new_id,
                    old_slot=old_clip_slot,
                    new_slot=1,
                )
        current_model = [new_id, 0]
        if not model_only:
            current_clip = [new_id, 1]
    return workflow


def validate_i2i(loaded: LoadedWorkflow) -> None:
    if not loaded.bindings.input:
        raise I2IUnsupportedError("workflow does not declare input binding")
    if (
        loaded.bindings.input not in loaded.node_index_by_title
        and loaded.bindings.input not in loaded.raw_workflow
    ):
        raise WorkflowValidationError(
            f"input binding not found: {loaded.bindings.input}"
        )
