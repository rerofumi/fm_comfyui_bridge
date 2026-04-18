from fm_comfyui_bridge.lora_yaml import SdLoraYaml


class ConfigLoraYaml(SdLoraYaml):
    def lora_model_only(self, index: int = 0) -> bool:
        if "lora" not in self.data:
            return False
        return bool(self.data["lora"][index].get("model_only", False))
