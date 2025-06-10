import datetime
import importlib.resources
import io
import json
import random
import time
from pathlib import Path

import requests
from PIL import Image, PngImagePlugin

import fm_comfyui_bridge.config as config
from fm_comfyui_bridge.lora_yaml import SdLoraYaml
from .workflow import WorkflowTemplate

#
# ComfyUI API request
#

def send_request(prompt: dict, server_url: str = None) -> str | None:
    headers = {"Content-Type": "application/json"}
    url = server_url if server_url else config.COMFYUI_URL
    response = requests.post(
        f"{url}prompt",
        headers=headers,
        data=json.dumps({"prompt": prompt}).encode("utf-8"),
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return response.json()["prompt_id"]


def await_request(check_interval: float, retry_interval: float, server_url: str = None):
    url = server_url if server_url else config.COMFYUI_URL
    while True:
        time.sleep(check_interval)
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{url}queue", headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            time.sleep(retry_interval)
            continue
        json_data = response.json()
        if (
            len(json_data.get("queue_running", [])) == 0
            and len(json_data.get("queue_pending", [])) == 0
        ):
            break


def get_image(id: any, server_url: str = None, output_node: str = None):
    url = server_url if server_url else config.COMFYUI_URL
    if not output_node:
        output_node = config.COMFYUI_NODE_OUTPUT # Still used
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{url}history/{id}", headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    subdir = response.json()[id]["outputs"][output_node]["images"][0]["subfolder"]
    filename = response.json()[id]["outputs"][output_node]["images"][0]["filename"]
    headers = {"Content-Type": "application/json"}
    params = {"subfolder": subdir, "filename": filename}
    response = requests.get(f"{url}view", headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return Image.open(io.BytesIO(response.content))


def send_image(filename, upload_name=None, server_url: str = None):
    url = server_url if server_url else config.COMFYUI_URL
    if upload_name is None:
        upload_name = Path(filename).name
    picture = Image.open(filename).convert("RGBA")
    picture_data = io.BytesIO()
    picture.save(picture_data, format="PNG")
    picture_data.seek(0)
    files = {
        "image": (upload_name, picture_data, "image/png"),
        "overwrite": True,
    }
    response = requests.post(f"{url}upload/image", files=files)
    return response


def free(server_url: str = None):
    url = server_url if server_url else config.COMFYUI_URL
    data = {
        "unload_models": True,
        "free_memory": True,
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{url}free", headers=headers, json=data)
    return response


def list_models(folder: str, server_url: str = None):
    url = server_url if server_url else config.COMFYUI_URL
    response = requests.get(f"{url}models/{folder}")
    return json.loads(response.text)


#
# Image works
#

def save_image(
    image, posi=None, nega=None, filename=None, workspace=None, output_dir=None
):
    global workspace_dir
    if workspace is None:
        workspace = "./"
    if output_dir is None:
        output_dir = config.OUTPUTS_DIR # Still used
    output_dir = Path(workspace) / output_dir
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}.png"
    image_path = output_dir / filename
    if posi is not None or nega is not None:
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("parameters", f"{posi}\nNegative prompt: {nega}\n")
        image.save(image_path, "PNG", pnginfo=metadata)
    else:
        image.save(image_path)
    return image_path


def get_input_image_name():
    current_time = int(time.time())
    input_image_name = f"bridge_i2i_input_{current_time}.png"
    return input_image_name


#
# LoRA functions removed as they are now part of WorkflowTemplate
#

#
# Workflow builder
#

def t2i_request_build(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
) -> dict:
    wf = WorkflowTemplate("SDXL_Base_API.json")

    wf.set_input_by_title("Load Checkpoint", "ckpt_name", lora.checkpoint)
    wf.set_input_by_title("CLIP Text Encode (Positive Prompt)", "text", prompt) # Updated title
    wf.set_input_by_title("CLIP Text Encode (Negative Prompt)", "text", negative) # Updated title

    wf.set_input_by_title("SamplerCustom", "noise_seed", random.randint(1, 10000000000))
    wf.set_input_by_title("Empty Latent Image", "width", image_size[0])
    wf.set_input_by_title("Empty Latent Image", "height", image_size[1])

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    wf.set_input_by_title("Save Image", "filename_prefix", f"{current_date}/Bridge")

    sampling_value = "v_prediction" if lora.vpred else "eps"
    wf.set_input_by_title("ModelSamplingDiscrete", "sampling", sampling_value)

    if lora.steps is not None:
        # In SDXL_Base_API.json, node "12" is BasicScheduler for steps.
        wf.set_input_by_title("BasicScheduler", "steps", lora.steps)
    if lora.cfg is not None:
        # In SDXL_Base_API.json, node "10" is SamplerCustom for cfg.
        wf.set_input_by_title("SamplerCustom", "cfg", lora.cfg)

    if hasattr(lora, 'lora_num') and lora.lora_num > 0 :
        wf.insert_loras(lora, "Load Checkpoint")
    return wf.get_workflow()


def t2i_highreso_request_build(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
) -> dict:
    wf = WorkflowTemplate("SDXL_HighReso_API.json")

    wf.set_input_by_title("Load Checkpoint", "ckpt_name", lora.checkpoint)
    wf.set_input_by_title("Positive Prompt Text", "text", prompt) # Updated title
    wf.set_input_by_title("Negative Prompt Text", "text", negative) # Updated title

    # Removed loop for COMFYUI_NODE_HR_SEED, now using unique titles
    wf.set_input_by_title("KSampler (Base Pass)", "seed", random.randint(1, 10000000000)) # Updated title
    wf.set_input_by_title("KSampler (Hi-Res Pass)", "seed", random.randint(1, 10000000000)) # Updated title
    # TODO: Add steps and cfg for these KSamplers if they are part of lora object and need setting
    # For example:
    # if hasattr(lora, 'base_steps') and lora.base_steps is not None:
    #     wf.set_input_by_title("KSampler (Base Pass)", "steps", lora.base_steps)
    # if hasattr(lora, 'base_cfg') and lora.base_cfg is not None:
    #     wf.set_input_by_title("KSampler (Base Pass)", "cfg", lora.base_cfg)
    # if hasattr(lora, 'hires_steps') and lora.hires_steps is not None:
    #     wf.set_input_by_title("KSampler (Hi-Res Pass)", "steps", lora.hires_steps)
    # if hasattr(lora, 'hires_cfg') and lora.hires_cfg is not None:
    #     wf.set_input_by_title("KSampler (Hi-Res Pass)", "cfg", lora.hires_cfg)

    wf.set_input_by_title("Width", "value", image_size[0]) # For initial latent
    wf.set_input_by_title("Hight", "value", image_size[1]) # For initial latent ("Hight" is the title in JSON)

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    wf.set_input_by_title("Save Image", "filename_prefix", f"{current_date}/Bridge")

    sampling_value = "v_prediction" if lora.vpred else "eps"
    # Removed loop for COMFYUI_NODE_HR_SAMPLING_DISCRETE
    # Assuming "ModelSamplingDiscrete" is the single node to control this for the whole graph.
    wf.set_input_by_title("ModelSamplingDiscrete", "sampling", sampling_value)

    if hasattr(lora, 'lora_num') and lora.lora_num > 0 :
        wf.insert_loras(lora, "Load Checkpoint")
    return wf.get_workflow()


def i2i_highreso_request_build(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    upload_image: str,
    image_size: tuple[int, int], # image_size is not used to set latent size directly
) -> dict:
    wf = WorkflowTemplate("SDXL_HighReso_I2I_API.json")

    wf.set_input_by_title("Load Checkpoint", "ckpt_name", lora.checkpoint)
    wf.set_input_by_title("Positive Prompt Text", "text", prompt) # Updated title
    wf.set_input_by_title("Negative Prompt Text", "text", negative) # Updated title

    # Removed loop for COMFYUI_NODE_HR_SEED, now using unique titles
    wf.set_input_by_title("KSampler (Base Pass)", "seed", random.randint(1, 10000000000)) # Updated title
    wf.set_input_by_title("KSampler (Hi-Res Pass)", "seed", random.randint(1, 10000000000)) # Updated title
    # TODO: Add steps and cfg for these KSamplers if they are part of lora object

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    wf.set_input_by_title("Save Image", "filename_prefix", f"{current_date}/Bridge")

    wf.set_input_by_title("Load Image", "image", upload_image)

    sampling_value = "v_prediction" if lora.vpred else "eps"
    # Removed loop for COMFYUI_NODE_HR_SAMPLING_DISCRETE
    wf.set_input_by_title("ModelSamplingDiscrete", "sampling", sampling_value)

    if hasattr(lora, 'lora_num') and lora.lora_num > 0 :
        wf.insert_loras(lora, "Load Checkpoint")
    return wf.get_workflow()


#
# convenience methods
#
def generate(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
    server_url: str = None,
) -> Image | None:
    id = None
    request_payload = t2i_request_build(prompt, negative, lora, image_size)
    id = send_request(request_payload, server_url=server_url)
    if id:
        await_request(1, 3, server_url=server_url)
        return get_image(
            id, output_node=config.COMFYUI_NODE_OUTPUT, server_url=server_url
        )
    return None


def generate_highreso(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
    server_url: str = None,
) -> Image | None:
    id = None
    request_payload = t2i_highreso_request_build(prompt, negative, lora, image_size)
    id = send_request(request_payload, server_url=server_url)
    if id:
        await_request(1, 3, server_url=server_url)
        return get_image(
            id, output_node=config.COMFYUI_NODE_HR_OUTPUT, server_url=server_url
        )
    return None


def generate_i2i_highreso(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
    input_image_filepath: str,
    server_url: str = None,
) -> Image | None:
    upload_image_filename = get_input_image_name()
    send_image(input_image_filepath, upload_name=upload_image_filename, server_url=server_url)

    request_payload = i2i_highreso_request_build(
        prompt, negative, lora, upload_image_filename, image_size
    )
    id = None
    id = send_request(request_payload, server_url=server_url)
    if id:
        await_request(1, 3, server_url=server_url)
        return get_image(
            id, output_node=config.COMFYUI_NODE_HR_OUTPUT, server_url=server_url
        )
    return None
