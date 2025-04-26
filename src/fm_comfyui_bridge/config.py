# API endpoint of ComfyUI
COMFYUI_URL = "http://127.0.0.1:8188/"

# ComfyUI model checkpoint
COMFYUI_USE_CHECKPOINT = "illustriousXL_v01.safetensors"
# ComfyUI checkpoint node
COMFYUI_NODE_CHECKPOINT = "4"
COMFYUI_NODE_HR_CHECKPOINT = "1"
# ComfyUI LoRA checkpoint node
COMFYUI_NODE_LORA_CHECKPOINT = "19"
COMFYUI_NODE_HR_LORA_CHECKPOINT = [("14", 1.0)]
# ComfyUI prompt node
COMFYUI_NODE_PROMPT = "6"
COMFYUI_NODE_HR_PROMPT = "4"
# ComfyUI negative prompt node
COMFYUI_NODE_NEGATIVE = "7"
COMFYUI_NODE_HR_NEGATIVE = "6"
# ComfyUI seed node
COMFYUI_NODE_SEED = "10"
COMFYUI_NODE_HR_SEED = ["7", "37"]
# ComfyUI output node
COMFYUI_NODE_OUTPUT = "26"
COMFYUI_NODE_HR_OUTPUT = "21"
# ComfyUI latent size node
COMFYUI_NODE_SIZE = "15"
COMFYUI_NODE_HR_SIZE_WIDTH = "30"
COMFYUI_NODE_HR_SIZE_HEIGHT = "32"
# ComfyUI sampling mode node
COMFYUI_NODE_SAMPLING_DISCRETE = "16"
COMFYUI_NODE_HR_SAMPLING_DISCRETE = ["22"]
# ComfyUI load image node
COMFYUI_NODE_HR_LOAD_IMAGE = "42"
# ComfyUI sampling node
COMFYUI_NODE_SAMPLING_STEPS = "12"
COMFYUI_NODE_SAMPLING_CFG = "10"

OUTPUTS_DIR = "./outputs/"
