import json
from pathlib import Path

from fm_comfy_request.config_lora_yaml import ConfigLoraYaml
from fm_comfy_request.models import (
    GeneratedImage,
    GenerationResult,
    LoadedWorkflow,
    WorkflowBindingSet,
)
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
    return LoadedWorkflow(
        path=Path("workflow.json"),
        raw_workflow=workflow,
        bindings=bindings,
        node_index_by_id=node_index_by_id,
        node_index_by_title=node_index_by_title,
    )


def test_parse_binding_yaml_normalizes_aliases():
    node = {
        "inputs": {"text": "model: model\nnegative_prompt: neg\nsamplingーmode: eps"}
    }
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
        "1": {
            "inputs": {"ckpt_name": "base.safetensors"},
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "model"},
        },
        "2": {
            "inputs": {"model": ["1", 0], "clip": ["1", 1]},
            "class_type": "KSampler",
            "_meta": {"title": "sampler"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded(workflow, bindings)
    lora = ConfigLoraYaml(
        data={"lora": [{"enabled": True, "model": "a.safetensors", "strength": 1.0}]}
    )
    result = insert_loras(loaded, workflow, lora)
    assert any(node["class_type"] == "LoraLoader" for node in result.values())
    sampler = result["2"]
    assert sampler["inputs"]["model"][0] != "1"


def test_insert_model_only_lora():
    workflow = {
        "1": {
            "inputs": {"ckpt_name": "base.safetensors"},
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "model"},
        },
        "2": {
            "inputs": {"model": ["1", 0]},
            "class_type": "SamplerCustom",
            "_meta": {"title": "sampler"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded(workflow, bindings)
    lora = ConfigLoraYaml(
        data={
            "lora": [
                {
                    "enabled": True,
                    "model": "a.safetensors",
                    "strength": 1.0,
                    "model_only": True,
                }
            ]
        }
    )
    result = insert_loras(loaded, workflow, lora)
    assert any(node["class_type"] == "LoraLoaderModelOnly" for node in result.values())
    assert result["2"]["inputs"]["model"][0] != "1"


def test_insert_lora_preserves_vae_link():
    workflow = {
        "1": {
            "inputs": {"ckpt_name": "base.safetensors"},
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "model"},
        },
        "2": {
            "inputs": {"model": ["1", 0], "clip": ["1", 1]},
            "class_type": "KSampler",
            "_meta": {"title": "sampler"},
        },
        "3": {
            "inputs": {"vae": ["1", 2]},
            "class_type": "VAEDecode",
            "_meta": {"title": "vae_decode"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded(workflow, bindings)
    lora = ConfigLoraYaml(
        data={"lora": [{"enabled": True, "model": "a.safetensors", "strength": 1.0}]}
    )
    result = insert_loras(loaded, workflow, lora)
    lora_node_id = next(
        nid for nid, n in result.items() if n["class_type"] == "LoraLoader"
    )
    assert result["2"]["inputs"]["model"][0] == lora_node_id
    assert result["2"]["inputs"]["clip"][0] == lora_node_id
    assert result["3"]["inputs"]["vae"] == ["1", 2]


def test_insert_model_only_lora_preserves_vae_link():
    workflow = {
        "1": {
            "inputs": {"ckpt_name": "base.safetensors"},
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "model"},
        },
        "2": {
            "inputs": {"model": ["1", 0]},
            "class_type": "SamplerCustom",
            "_meta": {"title": "sampler"},
        },
        "3": {
            "inputs": {"vae": ["1", 2]},
            "class_type": "VAEDecode",
            "_meta": {"title": "vae_decode"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model")
    loaded = _loaded(workflow, bindings)
    lora = ConfigLoraYaml(
        data={
            "lora": [
                {
                    "enabled": True,
                    "model": "a.safetensors",
                    "strength": 1.0,
                    "model_only": True,
                }
            ]
        }
    )
    result = insert_loras(loaded, workflow, lora)
    lora_node_id = next(
        nid for nid, n in result.items() if n["class_type"] == "LoraLoaderModelOnly"
    )
    assert result["2"]["inputs"]["model"][0] == lora_node_id
    assert result["3"]["inputs"]["vae"] == ["1", 2]


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
        "1": {
            "inputs": {"noise_seed": 1},
            "class_type": "SamplerCustom",
            "_meta": {"title": "sampler"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model", seed="sampler")
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, seed=42)
    assert result["1"]["inputs"]["noise_seed"] == 42


def test_apply_overrides_updates_bound_denoise():
    workflow = {
        "1": {
            "inputs": {"denoise": 0.72},
            "class_type": "BasicScheduler",
            "_meta": {"title": "BasicScheduler"},
        },
    }
    bindings = WorkflowBindingSet(
        meta_node_id="meta", model="model", denoise="BasicScheduler"
    )
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, denoise=0.45)
    assert result["1"]["inputs"]["denoise"] == 0.45


def test_apply_overrides_falls_back_to_seed_input_name():
    workflow = {
        "1": {
            "inputs": {"seed": 1},
            "class_type": "KSampler",
            "_meta": {"title": "sampler"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="model", seed="sampler")
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, seed=42)
    assert result["1"]["inputs"]["seed"] == 42
    assert "noise_seed" not in result["1"]["inputs"]


def test_apply_overrides_updates_checkpoint_loader_model_name():
    workflow = {
        "1": {
            "inputs": {"ckpt_name": "base.safetensors"},
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "Load Checkpoint"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="Load Checkpoint")
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, model="new-base.safetensors")
    assert result["1"]["inputs"]["ckpt_name"] == "new-base.safetensors"


def test_apply_overrides_updates_unet_loader_model_name():
    workflow = {
        "44": {
            "inputs": {
                "unet_name": "anima\\animaOfficial_preview3Base.safetensors",
                "weight_dtype": "default",
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "Load Diffusion Model"},
        },
    }
    bindings = WorkflowBindingSet(meta_node_id="meta", model="Load Diffusion Model")
    loaded = _loaded(workflow, bindings)
    result = apply_overrides(loaded, model="anima\\new.safetensors")
    assert result["44"]["inputs"]["unet_name"] == "anima\\new.safetensors"


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


def test_cli_generate_passes_model_override(monkeypatch):
    from fm_comfy_request import cli

    captured = {}

    class Result:
        images = []

    def fake_generate(_workflow, **kwargs):
        captured["model"] = kwargs.get("model")
        return Result()

    monkeypatch.setattr(cli, "generate", fake_generate)

    assert cli.main(["generate", "workflow.json", "--model", "base.safetensors"]) == 0
    assert captured == {"model": "base.safetensors"}


def test_cli_generate_i2i_passes_denoise_override(monkeypatch):
    from fm_comfy_request import cli

    captured = {}

    def fake_generate_i2i(_workflow, _input_image, **kwargs):
        captured["denoise"] = kwargs.get("denoise")
        return GenerationResult(
            prompt_id="prompt-1",
            client_id="client-1",
            workflow_path=Path("workflow.json"),
            workflow_final={},
            output_node_id=None,
        )

    monkeypatch.setattr(cli, "generate_i2i", fake_generate_i2i)

    assert (
        cli.main(["generate-i2i", "workflow.json", "input.png", "--denoise", "0.45"])
        == 0
    )
    assert captured == {"denoise": 0.45}


def test_cli_generate_i2i_writes_output_file(tmp_path, monkeypatch):
    from fm_comfy_request import cli

    output = tmp_path / "out.png"

    def fake_generate_i2i(_workflow, _input_image, **_kwargs):
        return GenerationResult(
            prompt_id="prompt-1",
            client_id="client-1",
            workflow_path=Path("workflow.json"),
            workflow_final={},
            output_node_id="9",
            images=[
                GeneratedImage(
                    filename="out.png",
                    subfolder="",
                    type="output",
                    image_bytes=b"png-bytes",
                )
            ],
        )

    monkeypatch.setattr(cli, "generate_i2i", fake_generate_i2i)

    assert (
        cli.main(
            [
                "generate-i2i",
                "workflow.json",
                "input.png",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert output.read_bytes() == b"png-bytes"


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
                "1": {
                    "inputs": {"ckpt_name": "base.safetensors"},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "model"},
                },
                "9": {
                    "inputs": {},
                    "class_type": "SaveImage",
                    "_meta": {"title": "Save Image"},
                },
                "36": {
                    "inputs": {"value": "model: model\noutput: Save Image"},
                    "class_type": "PrimitiveStringMultiline",
                    "_meta": {"title": "fm_comfy_request"},
                },
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
            return {
                "prompt-1": {
                    "outputs": {
                        "9": {
                            "images": [
                                {
                                    "filename": "out.png",
                                    "subfolder": "",
                                    "type": "output",
                                }
                            ]
                        }
                    }
                }
            }

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
                "1": {
                    "inputs": {"ckpt_name": "base.safetensors"},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "model"},
                },
                "2": {
                    "inputs": {"noise_seed": 1},
                    "class_type": "SamplerCustom",
                    "_meta": {"title": "SamplerCustom"},
                },
                "36": {
                    "inputs": {"value": "model: model\nseed: SamplerCustom"},
                    "class_type": "PrimitiveStringMultiline",
                    "_meta": {"title": "fm_comfy_request"},
                },
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
                "1": {
                    "inputs": {"ckpt_name": "base.safetensors"},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "model"},
                },
                "2": {
                    "inputs": {"noise_seed": 1},
                    "class_type": "SamplerCustom",
                    "_meta": {"title": "SamplerCustom"},
                },
                "36": {
                    "inputs": {"value": "model: model\nseed: SamplerCustom"},
                    "class_type": "PrimitiveStringMultiline",
                    "_meta": {"title": "fm_comfy_request"},
                },
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

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate(
        "workflow.json", random_seed=False
    )

    assert submitted["seed"] == 1
    assert result.workflow_final["2"]["inputs"]["noise_seed"] == 1


def test_client_applies_config_model_to_checkpoint_loader(tmp_path, monkeypatch):
    from fm_comfy_request import client

    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "1": {
                    "inputs": {"ckpt_name": "base.safetensors"},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "model"},
                },
                "36": {
                    "inputs": {"value": "model: model"},
                    "class_type": "PrimitiveStringMultiline",
                    "_meta": {"title": "fm_comfy_request"},
                },
            }
        ),
        encoding="utf-8",
    )
    submitted = {}

    class FakeTransport:
        def __init__(self, *_args, **_kwargs):
            pass

        def submit_prompt(self, workflow, _client_id):
            submitted["ckpt_name"] = workflow["1"]["inputs"]["ckpt_name"]
            return "prompt-1"

        def watch(self, *_args, **_kwargs):
            return None

        def history(self, _prompt_id):
            return {"prompt-1": {"outputs": {}}}

    monkeypatch.setattr(client, "Transport", FakeTransport)
    lora = ConfigLoraYaml(data={"checkpoint": "new-base.safetensors"})

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate(
        "workflow.json", lora=lora
    )

    assert submitted["ckpt_name"] == "new-base.safetensors"
    assert result.workflow_final["1"]["inputs"]["ckpt_name"] == "new-base.safetensors"


def test_client_applies_config_model_to_unet_loader(tmp_path, monkeypatch):
    from fm_comfy_request import client

    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "44": {
                    "inputs": {"unet_name": "anima\\old.safetensors"},
                    "class_type": "UNETLoader",
                    "_meta": {"title": "Load Diffusion Model"},
                },
                "54": {
                    "inputs": {"value": 'model: "Load Diffusion Model"'},
                    "class_type": "PrimitiveStringMultiline",
                    "_meta": {"title": "fm_comfy_request"},
                },
            }
        ),
        encoding="utf-8",
    )
    submitted = {}

    class FakeTransport:
        def __init__(self, *_args, **_kwargs):
            pass

        def submit_prompt(self, workflow, _client_id):
            submitted["unet_name"] = workflow["44"]["inputs"]["unet_name"]
            return "prompt-1"

        def watch(self, *_args, **_kwargs):
            return None

        def history(self, _prompt_id):
            return {"prompt-1": {"outputs": {}}}

    monkeypatch.setattr(client, "Transport", FakeTransport)
    lora = ConfigLoraYaml(data={"model": "anima\\new.safetensors"})

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate(
        "workflow.json", lora=lora
    )

    assert submitted["unet_name"] == "anima\\new.safetensors"
    assert result.workflow_final["44"]["inputs"]["unet_name"] == "anima\\new.safetensors"


def test_client_applies_denoise_override(tmp_path, monkeypatch):
    from fm_comfy_request import client

    workflow_path = tmp_path / "workflow.json"
    workflow_path.write_text(
        json.dumps(
            {
                "1": {
                    "inputs": {"ckpt_name": "base.safetensors"},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "model"},
                },
                "2": {
                    "inputs": {"denoise": 0.72},
                    "class_type": "BasicScheduler",
                    "_meta": {"title": "BasicScheduler"},
                },
                "3": {
                    "inputs": {"image": "input.png"},
                    "class_type": "LoadImage",
                    "_meta": {"title": "Load Image"},
                },
                "36": {
                    "inputs": {
                        "value": "model: model\ninput: Load Image\ndenoise: BasicScheduler"
                    },
                    "class_type": "PrimitiveStringMultiline",
                    "_meta": {"title": "fm_comfy_request"},
                },
            }
        ),
        encoding="utf-8",
    )
    submitted = {}

    class FakeTransport:
        def __init__(self, *_args, **_kwargs):
            pass

        def submit_prompt(self, workflow, _client_id):
            submitted["denoise"] = workflow["2"]["inputs"]["denoise"]
            return "prompt-1"

        def upload_image(self, _name, _image_bytes):
            return {"name": _name}

        def watch(self, *_args, **_kwargs):
            return None

        def history(self, _prompt_id):
            return {"prompt-1": {"outputs": {}}}

    monkeypatch.setattr(client, "Transport", FakeTransport)

    result = client.ComfyRequestClient(workflow_dir=tmp_path).generate_i2i(
        "workflow.json", b"png", denoise=0.45
    )

    assert submitted["denoise"] == 0.45
    assert result.workflow_final["2"]["inputs"]["denoise"] == 0.45
