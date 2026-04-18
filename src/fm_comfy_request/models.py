from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ClientSettings:
    server_url: str
    workflow_dir: Path
    timeout_seconds: float = 120.0
    retry_count: int = 2
    retry_interval_seconds: float = 1.0
    connect_timeout_seconds: float = 10.0


@dataclass(slots=True)
class GenerationOverrides:
    prompt: str | None = None
    negative: str | None = None
    seed: int | None = None
    width: int | None = None
    height: int | None = None
    steps: int | None = None
    cfg: float | None = None
    sampling_mode: str | None = None
    server_url: str | None = None


@dataclass(slots=True)
class NodeRef:
    node_id: str
    title: str | None = None
    class_type: str | None = None
    input_name: str | None = None
    model_output_index: int = 0
    clip_output_index: int | None = None


@dataclass(slots=True)
class WorkflowBindingSet:
    meta_node_id: str
    model: str
    clip: str | None = None
    prompt: str | None = None
    negative_prompt: str | None = None
    seed: str | None = None
    output: str | None = None
    input: str | None = None
    size: str | None = None
    size_width: str | None = None
    size_height: str | None = None
    sampling_mode: str | None = None
    steps: str | None = None
    cfg: str | None = None
    seed_name: str = "noise_seed"


@dataclass(slots=True)
class LoadedWorkflow:
    path: Path
    raw_workflow: dict[str, Any]
    bindings: WorkflowBindingSet
    node_index_by_id: dict[str, dict[str, Any]]
    node_index_by_title: dict[str, list[str]]


@dataclass(slots=True)
class GeneratedImage:
    filename: str
    subfolder: str
    type: str
    image_bytes: bytes


@dataclass(slots=True)
class GenerationResult:
    prompt_id: str
    client_id: str
    workflow_path: Path
    workflow_final: dict[str, Any]
    output_node_id: str | None
    images: list[GeneratedImage] = field(default_factory=list)
    history: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProgressEvent:
    prompt_id: str | None
    event_type: str
    node_id: str | None
    value: Any = None
    max_value: Any = None
    message: str | None = None
    raw_event: dict[str, Any] = field(default_factory=dict)
