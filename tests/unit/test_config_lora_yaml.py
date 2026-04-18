from fm_comfy_request.config_lora_yaml import ConfigLoraYaml


def test_model_only_defaults_false():
    cfg = ConfigLoraYaml(data={"lora": [{"enabled": True, "model": "a.safetensors", "strength": 1.0}]})
    assert cfg.lora_model_only(0) is False


def test_model_only_reads_true():
    cfg = ConfigLoraYaml(data={"lora": [{"enabled": True, "model": "a.safetensors", "strength": 1.0, "model_only": True}]})
    assert cfg.lora_model_only(0) is True

