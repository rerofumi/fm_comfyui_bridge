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
        output_dir = config.OUTPUTS_DIR
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
# LoRA ノード差し込み
#


def replace_value_recursive(data, old_value, new_value):
    """
    辞書やリスト内の特定の値を再帰的に置換し、新しいオブジェクトを返す。

    Args:
        data: 処理対象の辞書またはリスト。
        old_value: 置換前の値。
        new_value: 置換後の値。

    Returns:
        値が置換された新しい辞書またはリスト。
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if value == old_value:
                new_dict[key] = new_value
            # 値が辞書かリストなら再帰呼び出し
            elif isinstance(value, (dict, list)):
                new_dict[key] = replace_value_recursive(value, old_value, new_value)
            else:
                # その他の型はそのままコピー
                new_dict[key] = value
        return new_dict
    elif isinstance(data, list):
        if data == [old_value, 0] or data == [old_value, 1]:
            return [new_value, data[1]]
        new_list = []
        for item in data:
            # 要素が辞書かリストなら再帰呼び出し
            if isinstance(item, (dict, list)):
                new_list.append(replace_value_recursive(item, old_value, new_value))
            else:
                # その他の型はそのままコピー
                new_list.append(item)
        return new_list
    else:
        # 辞書でもリストでもない場合はそのまま返す
        return data


def get_new_node_num(workflow: dict):
    node_num = 0
    for node in workflow:
        num = int(node)
        if num > node_num:
            node_num = num
    return node_num + 1


def add_lora(workflow: dict, lora: SdLoraYaml, index: int, checkpoint: str = None):
    lora_node = {}
    lora_node_num = str(get_new_node_num(workflow))
    lora_node[lora_node_num] = {
        "inputs": {
            "lora_name": lora.lora_model(index),
            "trigger": lora.lora_trigger(index),
            "strength_model": lora.lora_strength(index),
            "strength_clip": lora.lora_strength(index),
            "model": [checkpoint, 0],
            "clip": [checkpoint, 1],
        },
        "class_type": "LoraLoader",
        "_meta": {"title": "Load LoRA"},
    }
    workflow |= lora_node
    # insert node
    new_workflow = {}
    for index, node in workflow.items():
        if index is checkpoint or index is lora_node_num:
            new_workflow[index] = node
            continue
        new_workflow[index] = replace_value_recursive(node, checkpoint, lora_node_num)
    return new_workflow


def insert_loras(workflow: dict, lora: SdLoraYaml, checkpoint: str = None):
    lora_num = lora.lora_num
    for i in range(lora_num):
        if lora.lora_enabled_flag(i):
            workflow = add_lora(workflow, lora, i, checkpoint)
    return workflow


#
# Workflow builder
#


def t2i_request_build(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
) -> any:
    with importlib.resources.open_text(
        "fm_comfyui_bridge.Workflow", "SDXL_Base_API.json"
    ) as f:
        workflow_node = json.load(f)
    # パラメータ埋め込み(workflowによって異なる処理)
    workflow_node[config.COMFYUI_NODE_CHECKPOINT]["inputs"]["ckpt_name"] = (
        lora.checkpoint
    )
    workflow_node[config.COMFYUI_NODE_PROMPT]["inputs"]["text"] = prompt
    workflow_node[config.COMFYUI_NODE_NEGATIVE]["inputs"]["text"] = negative
    workflow_node[config.COMFYUI_NODE_SEED]["inputs"]["noise_seed"] = random.randint(
        1, 10000000000
    )
    workflow_node[config.COMFYUI_NODE_SIZE]["inputs"]["width"] = image_size[0]
    workflow_node[config.COMFYUI_NODE_SIZE]["inputs"]["height"] = image_size[1]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    workflow_node[config.COMFYUI_NODE_OUTPUT]["inputs"]["filename_prefix"] = (
        f"{current_date}/Bridge"
    )
    # prediction
    if lora.vpred:
        workflow_node[config.COMFYUI_NODE_SAMPLING_DISCRETE]["inputs"]["sampling"] = (
            "v_prediction"
        )
    else:
        workflow_node[config.COMFYUI_NODE_SAMPLING_DISCRETE]["inputs"]["sampling"] = (
            "eps"
        )
    if lora.steps is not None:
        workflow_node[config.COMFYUI_NODE_SAMPLING_STEPS]["inputs"]["steps"] = (
            lora.steps
        )
    if lora.cfg is not None:
        workflow_node[config.COMFYUI_NODE_SAMPLING_CFG]["inputs"]["cfg"] = lora.cfg
    # lora
    workflow_node = insert_loras(workflow_node, lora, config.COMFYUI_NODE_CHECKPOINT)
    return workflow_node


def t2i_highreso_request_build(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
) -> any:
    with importlib.resources.open_text(
        "fm_comfyui_bridge.Workflow", "SDXL_HighReso_API.json"
    ) as f:
        workflow_node = json.load(f)
    # パラメータ埋め込み(workflowによって異なる処理)
    workflow_node[config.COMFYUI_NODE_HR_CHECKPOINT]["inputs"]["ckpt_name"] = (
        lora.checkpoint
    )
    workflow_node[config.COMFYUI_NODE_HR_PROMPT]["inputs"]["text"] = prompt
    workflow_node[config.COMFYUI_NODE_HR_NEGATIVE]["inputs"]["text"] = negative
    for node in config.COMFYUI_NODE_HR_SEED:
        workflow_node[node]["inputs"]["seed"] = random.randint(1, 10000000000)
    workflow_node[config.COMFYUI_NODE_HR_SIZE_WIDTH]["inputs"]["value"] = image_size[0]
    workflow_node[config.COMFYUI_NODE_HR_SIZE_HEIGHT]["inputs"]["value"] = image_size[1]
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    workflow_node[config.COMFYUI_NODE_HR_OUTPUT]["inputs"]["filename_prefix"] = (
        f"{current_date}/Bridge"
    )
    # prediction
    if lora.vpred:
        for node in config.COMFYUI_NODE_HR_SAMPLING_DISCRETE:
            workflow_node[node]["inputs"]["sampling"] = "v_prediction"
    else:
        for node in config.COMFYUI_NODE_HR_SAMPLING_DISCRETE:
            workflow_node[node]["inputs"]["sampling"] = "eps"
    # lora
    workflow_node = insert_loras(workflow_node, lora, config.COMFYUI_NODE_HR_CHECKPOINT)
    return workflow_node


def i2i_highreso_request_build(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    upload_image: str,
    image_size: tuple[int, int],
) -> any:
    with importlib.resources.open_text(
        "fm_comfyui_bridge.Workflow", "SDXL_HighReso_I2I_API.json"
    ) as f:
        workflow_node = json.load(f)
    # パラメータ埋め込み(workflowによって異なる処理)
    workflow_node[config.COMFYUI_NODE_HR_CHECKPOINT]["inputs"]["ckpt_name"] = (
        lora.checkpoint
    )
    workflow_node[config.COMFYUI_NODE_HR_PROMPT]["inputs"]["text"] = prompt
    workflow_node[config.COMFYUI_NODE_HR_NEGATIVE]["inputs"]["text"] = negative
    for node in config.COMFYUI_NODE_HR_SEED:
        workflow_node[node]["inputs"]["seed"] = random.randint(1, 10000000000)
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    workflow_node[config.COMFYUI_NODE_HR_OUTPUT]["inputs"]["filename_prefix"] = (
        f"{current_date}/Bridge"
    )
    # upload image
    workflow_node[config.COMFYUI_NODE_HR_LOAD_IMAGE]["inputs"]["image"] = upload_image
    # prediction
    if lora.vpred:
        for node in config.COMFYUI_NODE_HR_SAMPLING_DISCRETE:
            workflow_node[node]["inputs"]["sampling"] = "v_prediction"
    else:
        for node in config.COMFYUI_NODE_HR_SAMPLING_DISCRETE:
            workflow_node[node]["inputs"]["sampling"] = "eps"
    # lora
    workflow_node = insert_loras(workflow_node, lora, config.COMFYUI_NODE_HR_CHECKPOINT)
    return workflow_node


#
# convenience methods
#
def generate(
    prompt: str,
    negative: str,
    lora: SdLoraYaml,
    image_size: tuple[int, int],
    server_url: str = None,
) -> Image:
    id = None
    id = send_request(
        t2i_request_build(prompt, negative, lora, image_size), server_url=server_url
    )
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
) -> Image:
    id = None
    id = send_request(
        t2i_highreso_request_build(prompt, negative, lora, image_size),
        server_url=server_url,
    )
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
) -> Image:
    # input image upload
    upload_image = get_input_image_name()
    send_image(input_image_filepath, upload_name=upload_image, server_url=server_url)

    prompt = i2i_highreso_request_build(
        prompt, negative, lora, upload_image, image_size
    )
    #
    id = None
    id = send_request(prompt, server_url=server_url)
    if id:
        await_request(1, 3, server_url=server_url)
        return get_image(
            id, output_node=config.COMFYUI_NODE_HR_OUTPUT, server_url=server_url
        )
    return None
