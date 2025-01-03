import datetime
import io
import json
import os
import random
import time

import requests
from PIL import Image, PngImagePlugin

import fm_comfyui_bridge.comfy_api as comfy_api
import fm_comfyui_bridge.config as config
from fm_comfyui_bridge.lora_yaml import SdLoraYaml

#
# ComfyUI API request
#


def send_request(prompt: str, server_url: str = None) -> str | None:
    # APIにリクエスト送信
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt}
    url = server_url if server_url else config.COMFYUI_URL
    response = requests.post(
        f"{url}prompt",
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return response.json()["prompt_id"]


def await_request(check_interval: float, retry_interval: float, server_url: str = None):
    # 一定時間ごとにリクエストの状態を確認
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
        output_node = config.COMFYUI_NODE_OUTPUT
    # リクエストヒストリからファイル名を取得
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
        upload_name = os.path.basename(filename)
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
        output_dir = config.OUTPUTS_DIR
    output_dir = os.path.join(workspace, output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if filename is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}.png"
    image_path = os.path.join(output_dir, filename)
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
# Workflow builder
#


def t2i_request_build(
    workflow: str,
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
) -> any:
    prompt_path = json.loads(workflow)
    # パラメータ埋め込み(workflowによって異なる処理)
    prompt_path[config.COMFYUI_NODE_CHECKPOINT]["inputs"]["ckpt_name"] = lora.checkpoint
    prompt_path[config.COMFYUI_NODE_PROMPT]["inputs"]["text"] = prompt
    prompt_path[config.COMFYUI_NODE_NEGATIVE]["inputs"]["text"] = negative
    prompt_path[config.COMFYUI_NODE_SEED]["inputs"]["noise_seed"] = random.randint(
        1, 10000000000
    )
    prompt_path[config.COMFYUI_NODE_SIZE]["inputs"]["width"] = image_size[0]
    prompt_path[config.COMFYUI_NODE_SIZE]["inputs"]["height"] = image_size[1]
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["lora_name"] = lora.model
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_model"] = (
        lora.strength
    )
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_clip"] = (
        lora.strength
    )
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    prompt_path[config.COMFYUI_NODE_OUTPUT]["inputs"]["filename_prefix"] = (
        f"{current_date}/Bridge"
    )
    # lora, prediction
    if not lora.lora_enabled:
        prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_model"] = 0
        prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_clip"] = 0
    if lora.vpred:
        prompt_path[config.COMFYUI_NODE_SAMPLING_DISCRETE]["inputs"]["sampling"] = (
            "v_prediction"
        )
    else:
        prompt_path[config.COMFYUI_NODE_SAMPLING_DISCRETE]["inputs"]["sampling"] = "eps"

    return prompt_path


def t2i_highreso_request_build(
    workflow: str,
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
) -> any:
    prompt_path = json.loads(workflow)
    # パラメータ埋め込み(workflowによって異なる処理)
    prompt_path[config.COMFYUI_NODE_HR_CHECKPOINT]["inputs"]["ckpt_name"] = (
        lora.checkpoint
    )
    prompt_path[config.COMFYUI_NODE_HR_PROMPT]["inputs"]["text"] = prompt
    prompt_path[config.COMFYUI_NODE_HR_NEGATIVE]["inputs"]["text"] = negative
    for node in config.COMFYUI_NODE_HR_SEED:
        prompt_path[node]["inputs"]["noise_seed"] = random.randint(1, 10000000000)
    prompt_path[config.COMFYUI_NODE_HR_SIZE_WIDTH]["inputs"]["value"] = image_size[0]
    prompt_path[config.COMFYUI_NODE_HR_SIZE_HEIGHT]["inputs"]["value"] = image_size[1]
    for node in config.COMFYUI_NODE_HR_LORA_CHECKPOINT:
        prompt_path[node[0]]["inputs"]["lora_name"] = lora.model
        prompt_path[node[0]]["inputs"]["strength_model"] = lora.strength * node[1]
        prompt_path[node[0]]["inputs"]["strength_clip"] = lora.strength * node[1]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    prompt_path[config.COMFYUI_NODE_HR_OUTPUT]["inputs"]["filename_prefix"] = (
        f"{current_date}/Bridge"
    )
    # lora, prediction
    if not lora.lora_enabled:
        for node in config.COMFYUI_NODE_HR_LORA_CHECKPOINT:
            prompt_path[node[0]]["inputs"]["strength_model"] = 0
            prompt_path[node[0]]["inputs"]["strength_clip"] = 0
    if lora.vpred:
        for node in config.COMFYUI_NODE_HR_SAMPLING_DISCRETE:
            prompt_path[node]["inputs"]["sampling"] = "v_prediction"
    else:
        for node in config.COMFYUI_NODE_HR_SAMPLING_DISCRETE:
            prompt_path[node]["inputs"]["sampling"] = "eps"

    return prompt_path


#
# convenience methods
#
def generate(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> Image:
    id = None
    id = send_request(
        t2i_request_build(comfy_api.NORMAL_WORKFLOW, prompt, negative, lora, image_size)
    )
    if id:
        await_request(1, 3)
        return get_image(id, output_node=config.COMFYUI_NODE_OUTPUT)
    return None


def generate_highreso(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> Image:
    id = None
    id = send_request(
        t2i_highreso_request_build(
            comfy_api.HIGHRES_WORKFLOW, prompt, negative, lora, image_size
        )
    )
    if id:
        await_request(1, 3)
        return get_image(id, output_node=config.COMFYUI_NODE_HR_OUTPUT)
    return None


def generate_i2i_highreso(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
    input_image_filepath: str,
) -> Image:
    # input image upload
    upload_image = get_input_image_name()
    send_image(input_image_filepath, upload_name=upload_image)
    prompt = t2i_highreso_request_build(
        comfy_api.HIGHRES_I2I_WORKFLOW, prompt, negative, lora, image_size
    )
    prompt[config.COMFYUI_NODE_HR_LOAD_IMAGE]["inputs"]["image"] = upload_image
    #
    id = None
    id = send_request(prompt)
    if id:
        await_request(1, 3)
        return get_image(id, output_node=config.COMFYUI_NODE_HR_OUTPUT)
    return None
