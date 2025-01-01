import os

from fm_comfyui_bridge.bridge import generate, generate_highreso, save_image, send_image
from fm_comfyui_bridge.comfy_api import NEGATIVE
from fm_comfyui_bridge.lora_yaml import SdLoraYaml


def test_bridge_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate("1girl", NEGATIVE, lora, (1024, 1024))
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(path, upload_name="bridge_test.png")
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")


def test_bridge_highreso_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate_highreso("1girl", NEGATIVE, lora, (1024, 1024))
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(path, upload_name="bridge_test.png")
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")


def test_lora_yaml_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    # 読み込んだ lola ファイルの中身確認
    assert lora.lora_enabled, "lora enabled check failed"
    assert (
        lora.checkpoint == "noobaicyberfix_v20.safetensors"
    ), "checkpoint check failed"
    assert lora.image_size == (768, 1344), "image size check failed"
    assert lora.model == "lora-ix-tillhi-v1.safetensors", "model check failed"
    assert lora.trigger == "tillhi", "trigger check failed"
    assert lora.strength == 0.9, "strength check failed"
    #
    out_file_path = "./tests/lora2.yaml"
    lora.write_to_yaml(out_file_path)
    # ファイルが存在するか確認し、存在しなかったらエラーを発生
    assert os.path.exists(out_file_path), f"ファイルが存在しません: {out_file_path}"
    if os.path.exists(out_file_path):
        os.remove(out_file_path)  # yaml書き込み後、ファイル削除
