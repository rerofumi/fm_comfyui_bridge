# API endpoint of ComfyUI
COMFYUI_URL = "http://127.0.0.1:8188/"

# ComfyUI seed node for high-resolution workflows (list of node IDs for KSamplers)
# Used to iterate seed settings; actual node targeting within loop is by title "KSampler".
COMFYUI_NODE_HR_SEED = ["7", "37"]

# ComfyUI output node IDs used in get_image and generate functions
COMFYUI_NODE_OUTPUT = "26"
COMFYUI_NODE_HR_OUTPUT = "21"

# ComfyUI sampling mode node for high-resolution workflows (list of node IDs, typically for ModelSamplingDiscrete)
# Used to iterate sampling settings; actual node targeting within loop is by title "ModelSamplingDiscrete".
COMFYUI_NODE_HR_SAMPLING_DISCRETE = ["22"]

OUTPUTS_DIR = "./outputs/"
