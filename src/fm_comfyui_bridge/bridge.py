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


def send_request(prompt: str) -> str | None:
    # APIにリクエスト送信
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt}
    response = requests.post(
        f"{config.COMFYUI_URL}prompt",
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
    )
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return response.json()["prompt_id"]


def await_request(check_interval: float, retry_interval: float):
    # 一定時間ごとにリクエストの状態を確認
    while True:
        time.sleep(check_interval)
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{config.COMFYUI_URL}queue", headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            time.sleep(retry_interval)
            continue
        json_data = response.json()
        # json の queue_running, queue_pending が存在し、 list 長が両方 0 の場合は break
        if (
            len(json_data.get("queue_running", [])) == 0
            and len(json_data.get("queue_pending", [])) == 0
        ):
            break


def t2i_request(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> any:
    prompt_path = json.loads(comfy_api.API_NO_LORA)
    # パラメータ埋め込み(workflowによって異なる処理)
    prompt_path[config.COMFYUI_NODE_CHECKPOINT]["inputs"]["ckpt_name"] = lora.checkpoint
    prompt_path[config.COMFYUI_NODE_PROMPT]["inputs"]["text"] = prompt
    prompt_path[config.COMFYUI_NODE_NEGATIVE]["inputs"]["text"] = negative
    prompt_path[config.COMFYUI_NODE_SEED]["inputs"]["seed"] = random.randint(
        1, 10000000000
    )
    prompt_path[config.COMFYUI_NODE_SIZE_WIDTH]["inputs"]["int"] = image_size[0]
    prompt_path[config.COMFYUI_NODE_SIZE_HEIGHT]["inputs"]["int"] = image_size[1]
    request_id = send_request(prompt_path)
    return request_id


def t2i_request_lora(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> any:
    prompt_path = json.loads(comfy_api.API_WITH_LORA)
    # パラメータ埋め込み(workflowによって異なる処理)
    prompt_path[config.COMFYUI_NODE_CHECKPOINT]["inputs"]["ckpt_name"] = lora.checkpoint
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["lora_name"] = lora.model
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_model"] = (
        lora.strength
    )
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_clip"] = (
        lora.strength
    )
    prompt_path[config.COMFYUI_NODE_PROMPT]["inputs"]["text"] = prompt
    prompt_path[config.COMFYUI_NODE_NEGATIVE]["inputs"]["text"] = negative
    prompt_path[config.COMFYUI_NODE_SEED]["inputs"]["seed"] = random.randint(
        1, 10000000000
    )
    prompt_path[config.COMFYUI_NODE_SIZE_WIDTH]["inputs"]["int"] = image_size[0]
    prompt_path[config.COMFYUI_NODE_SIZE_HEIGHT]["inputs"]["int"] = image_size[1]
    request_id = send_request(prompt_path)
    return request_id


def t2i_request_vpred(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> any:
    prompt_path = json.loads(comfy_api.API_NO_LORA_VPRED)
    # パラメータ埋め込み(workflowによって異なる処理)
    prompt_path[config.COMFYUI_NODE_CHECKPOINT]["inputs"]["ckpt_name"] = lora.checkpoint
    prompt_path[config.COMFYUI_NODE_PROMPT]["inputs"]["text"] = prompt
    prompt_path[config.COMFYUI_NODE_NEGATIVE]["inputs"]["text"] = negative
    prompt_path[config.COMFYUI_NODE_VPRED_SEED]["inputs"]["noise_seed"] = (
        random.randint(1, 10000000000)
    )
    prompt_path[config.COMFYUI_NODE_SIZE_WIDTH]["inputs"]["int"] = image_size[0]
    prompt_path[config.COMFYUI_NODE_SIZE_HEIGHT]["inputs"]["int"] = image_size[1]
    request_id = send_request(prompt_path)
    return request_id


def t2i_request_vpred_lora(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> any:
    prompt_path = json.loads(comfy_api.API_WITH_LORA_VPRED)
    # パラメータ埋め込み(workflowによって異なる処理)
    prompt_path[config.COMFYUI_NODE_CHECKPOINT]["inputs"]["ckpt_name"] = lora.checkpoint
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["lora_name"] = lora.model
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_model"] = (
        lora.strength
    )
    prompt_path[config.COMFYUI_NODE_LORA_CHECKPOINT]["inputs"]["strength_clip"] = (
        lora.strength
    )
    prompt_path[config.COMFYUI_NODE_PROMPT]["inputs"]["text"] = prompt
    prompt_path[config.COMFYUI_NODE_NEGATIVE]["inputs"]["text"] = negative
    prompt_path[config.COMFYUI_NODE_VPRED_SEED]["inputs"]["noise_seed"] = (
        random.randint(1, 10000000000)
    )
    prompt_path[config.COMFYUI_NODE_SIZE_WIDTH]["inputs"]["int"] = image_size[0]
    prompt_path[config.COMFYUI_NODE_SIZE_HEIGHT]["inputs"]["int"] = image_size[1]
    request_id = send_request(prompt_path)
    return request_id


def get_image(id: any):
    # リクエストヒストリからファイル名を取得
    headers = {"Content-Type": "application/json"}
    response = requests.get(f"{config.COMFYUI_URL}history/{id}", headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    subdir = response.json()[id]["outputs"][config.COMFYUI_NODE_OUTPUT]["images"][0][
        "subfolder"
    ]
    filename = response.json()[id]["outputs"][config.COMFYUI_NODE_OUTPUT]["images"][0][
        "filename"
    ]
    # API で画像ファイルを取得
    headers = {"Content-Type": "application/json"}
    params = {"subfolder": subdir, "filename": filename}
    response = requests.get(f"{config.COMFYUI_URL}view", headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return Image.open(io.BytesIO(response.content))


def save_image(image, posi=None, nega=None, filename=None, workspace=None):
    global workspace_dir
    if workspace is None:
        workspace = "./"
    output_dir = os.path.join(workspace, config.OUTPUTS_DIR)
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


#
# convenience methods
#
def generate(
    prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]
) -> Image:
    id = None
    if lora.lora_enabled and lora.vprod:
        id = t2i_request_vpred_lora(prompt, negative, lora, image_size)
    elif not lora.lora_enabled and lora.vprod:
        id = t2i_request_vpred(prompt, negative, lora, image_size)
    elif lora.lora_enabled and not lora.vprod:
        id = t2i_request_lora(prompt, negative, lora, image_size)
    else:
        id = t2i_request(prompt, negative, lora, image_size)
    if id:
        await_request(1, 3)
        return get_image(id)
    return None
