# API endpoint of ComfyUI
COMFYUI_URL = "http://127.0.0.1:8188/"

# ComfyUI model checkpoint
COMFYUI_USE_CHECKPOINT = "illustriousXL_v01.safetensors"
# ComfyUI checkpoint node
COMFYUI_NODE_CHECKPOINT = "4"
COMFYUI_NODE_HR_CHECKPOINT = "5"
# ComfyUI LoRA checkpoint node
COMFYUI_NODE_LORA_CHECKPOINT = "19"
COMFYUI_NODE_HR_LORA_CHECKPOINT = [
    ("7", 0.6),
    ("32", 0.8),
    ("54", 0.9),
    ("67", 1.0),
    ("82", 1.0),
    ("133", 1.0),
]
# ComfyUI prompt node
COMFYUI_NODE_PROMPT = "6"
COMFYUI_NODE_HR_PROMPT = "1"
# ComfyUI negative prompt node
COMFYUI_NODE_NEGATIVE = "7"
COMFYUI_NODE_HR_NEGATIVE = "2"
# ComfyUI seed node
COMFYUI_NODE_SEED = "10"
COMFYUI_NODE_HR_SEED = ["20", "37", "53", "69", "84", "128"]
# ComfyUI output node
COMFYUI_NODE_OUTPUT = "26"
COMFYUI_NODE_HR_OUTPUT = "111"
# ComfyUI latent size node
COMFYUI_NODE_SIZE = "15"
COMFYUI_NODE_HR_SIZE_WIDTH = "164"
COMFYUI_NODE_HR_SIZE_HEIGHT = "165"
# ComfyUI sampling mode node
COMFYUI_NODE_SAMPLING_DISCRETE = "16"
COMFYUI_NODE_HR_SAMPLING_DISCRETE = ["12", "31", "48", "68", "83", "138"]
# ComfyUI load image node
COMFYUI_NODE_HR_LOAD_IMAGE = "123"

OUTPUTS_DIR = "./outputs/"
