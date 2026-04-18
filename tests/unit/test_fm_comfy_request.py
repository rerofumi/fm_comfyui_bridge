import json
from pathlib import Path

from fm_comfy_request.config_lora_yaml import ConfigLoraYaml
from fm_comfy_request.models import LoadedWorkflow, WorkflowBindingSet
from fm_comfy_request.workflow import (
    apply_overrides,
    build_bindings,
    build_indices,
    insert_loras,
    parse_binding_yaml,
    validate_i2i,
)


def _loaded(workflow, bindings):
    node_index_by_id, node_index_by_title = build_indices(workflow)
    return LoadedWorkflow(path=Path("workflow.json"), raw_workflow=workflow, bindings=bindings, node_index_by_id=node_index_by_id, node_index_by_title=node_index_by_title)


def test_parse_binding_yaml_normalizes_aliases():
    node = {"inputs": {"text": "model: model\nnegative_prompt: neg\nsamplingーmode: eps"}}
    parsed = parse_binding_yaml(node)
    assert parsed["negative-prompt"] == "neg"
    assert parsed["sampling-mode"] == "eps"


def test_build_bindings_requires_model():
    try:
        build_bindings({})
    except Exception as exc:
        assert "model" in str(exc)
    else:
        raise AssertionError("expected error")


def test_insert_clip_lora_rewires_model_and_clip():
    workflow = {
        "1": {"inputs": {"ckpt_name": "base.safetensors"}, "class_type": "CheckpointLoaderSimple", "_meta": {"title": "model"}},
        "2": {"inputs": {"model": ["1", 0], "clip": ["1", 1]}, "class_type": "KSampler", "_meta": {"title": "sampler"}},
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded(workflow, bindings)
    lora = ConfigLoraYaml(data={"lora": [{"enabled": True, "model": "a.safetensors", "strength": 1.0}]})
    result = insert_loras(loaded, workflow, lora)
    assert any(node["class_type"] == "LoraLoader" for node in result.values())
    sampler = result["2"]
    assert sampler["inputs"]["model"][0] != "1"


def test_insert_model_only_lora():
    workflow = {
        "1": {"inputs": {"ckpt_name": "base.safetensors"}, "class_type": "CheckpointLoaderSimple", "_meta": {"title": "model"}},
        "2": {"inputs": {"model": ["1", 0]}, "class_type": "SamplerCustom", "_meta": {"title": "sampler"}},
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded(workflow, bindings)
    lora = ConfigLoraYaml(data={"lora": [{"enabled": True, "model": "a.safetensors", "strength": 1.0, "model_only": True}]})
    result = insert_loras(loaded, workflow, lora)
    assert any(node["class_type"] == "LoraLoaderModelOnly" for node in result.values())
    assert result["2"]["inputs"]["model"][0] != "1"


def test_validate_i2i_requires_input_binding():
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded({}, bindings)
    try:
        validate_i2i(loaded)
    except Exception as exc:
        assert "input" in str(exc)
    else:
        raise AssertionError("expected error")



def test_apply_overrides_updates_bound_noise_seed():
    workflow = {
        "1": {"inputs": {"noise_seed": 1}, "class_type": "SamplerCustom", "_meta": {"title": "sampler"}},
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model", seed="sampler")
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, seed=42)
    assert result["1"]["inputs"]["noise_seed"] == 42


def test_apply_overrides_falls_back_to_seed_input_name():
    workflow = {
        "1": {"inputs": {"seed": 1}, "class_type": "KSampler", "_meta": {"title": "sampler"}},
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model", seed="sampler")
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, seed=42)
    assert result["1"]["inputs"]["seed"] == 42
    assert "noise_seed" not in result["1"]["inputs"]


def test_cli_generate_delegates_default_random_seed_to_client(monkeypatch):
    from fm_comfy_request import cli

    captured = {}

    class Result:
        images = []

    def fake_generate(workflow, **kwargs):
        captured["workflow"] = workflow
        captured["seed"] = kwargs.get("seed")
        captured["random_seed"] = kwargs.get("random_seed")
        return Result()

    monkeypatch.setattr(cli, "generate", fake_generate)

    assert cli.main(["generate", "workflow.json"]) == 0
    assert captured == {"workflow": "workflow.json", "seed": None, "random_seed": True}


def test_cli_generate_can_preserve_workflow_seed(monkeypatch):
    from fm_comfy_request import cli

    captured = {}

    class Result:
        images = []

    def fake_generate(_workflow, **kwargs):
        captured["seed"] = kwargs.get("seed")
        captured["random_seed"] = kwargs.get("random_seed")
        return Result()

    monkeypatch.setattr(cli, "generate", fake_generate)

    assert cli.main(["generate", "workflow.json", "--no-random-seed"]) == 0
    assert captured == {"seed": None, "random_seed": False}


def test_client_resolves_output_title_to_history_node_id(tmp_path, monkeypatch):
    from fm_comfy_request import client

    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "1": {"inputs": {"ckpt_name": "base.safetensors"}, "class_type": "CheckpointLoaderSimple", "_meta": {"title": "model"}},
                "9": {"inputs": {}, "class_type": "SaveImage", "_meta": {"title": "Save Image"}},
                "36": {"inputs": {"value": "model: model\noutput: Save Image"}, "class_type": "PrimitiveStringMultiline", "_meta": {"title": "fm_comfy_request"}},
            }
        ),
        encoding="utf-8",
    )

    class FakeTransport:
        def __init__(self, *_args, **_kwargs):
            pass

        def submit_prompt(self, _workflow, _client_id):
            return "prompt-1"

        def watch(self, *_args, **_kwargs):
            return None

        def history(self, _prompt_id):
            return {"prompt-1": {"outputs": {"9": {"images": [{"filename": "out.png", "subfolder": "", "type": "output"}]}}}}

        def view(self, _subfolder, _filename):
            return b"png"

    monkeypatch.setattr(client, "Transport", FakeTransport)

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate("workflow.json")

    assert result.output_node_id == "9"
    assert result.images[0].image_bytes == b"png"

def test_client_generates_random_seed_when_seed_is_omitted(tmp_path, monkeypatch):
    from fm_comfy_request import client

    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "1": {"inputs": {"ckpt_name": "base.safetensors"}, "class_type": "CheckpointLoaderSimple", "_meta": {"title": "model"}},
                "2": {"inputs": {"noise_seed": 1}, "class_type": "SamplerCustom", "_meta": {"title": "SamplerCustom"}},
                "36": {"inputs": {"value": "model: model\nseed: SamplerCustom"}, "class_type": "PrimitiveStringMultiline", "_meta": {"title": "fm_comfy_request"}},
            }
        ),
        encoding="utf-8",
    )
    submitted = {}

    class FakeTransport:
        def __init__(self, *_args, **_kwargs):
            pass

        def submit_prompt(self, workflow, _client_id):
            submitted["seed"] = workflow["2"]["inputs"]["noise_seed"]
            return "prompt-1"

        def watch(self, *_args, **_kwargs):
            return None

        def history(self, _prompt_id):
            return {"prompt-1": {"outputs": {}}}

    monkeypatch.setattr(client, "Transport", FakeTransport)
    monkeypatch.setattr(client.random, "randint", lambda _min, _max: 123)

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate("workflow.json")

    assert submitted["seed"] == 123
    assert result.workflow_final["2"]["inputs"]["noise_seed"] == 123


def test_client_can_preserve_workflow_seed(tmp_path, monkeypatch):
    from fm_comfy_request import client

    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "1": {"inputs": {"ckpt_name": "base.safetensors"}, "class_type": "CheckpointLoaderSimple", "_meta": {"title": "model"}},
                "2": {"inputs": {"noise_seed": 1}, "class_type": "SamplerCustom", "_meta": {"title": "SamplerCustom"}},
                "36": {"inputs": {"value": "model: model\nseed: SamplerCustom"}, "class_type": "PrimitiveStringMultiline", "_meta": {"title": "fm_comfy_request"}},
            }
        ),
        encoding="utf-8",
    )
    submitted = {}

    class FakeTransport:
        def __init__(self, *_args, **_kwargs):
            pass

        def submit_prompt(self, workflow, _client_id):
            submitted["seed"] = workflow["2"]["inputs"]["noise_seed"]
            return "prompt-1"

        def watch(self, *_args, **_kwargs):
            return None

        def history(self, _prompt_id):
            return {"prompt-1": {"outputs": {}}}

    monkeypatch.setattr(client, "Transport", FakeTransport)

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate("workflow.json", random_seed=False)

    assert submitted["seed"] == 1
    assert result.workflow_final["2"]["inputs"]["noise_seed"] == 1