import os

from fm_comfyui_bridge.bridge import (
    free,
    generate,
    generate_highreso,
    generate_i2i_highreso,
    list_models,
    save_image,
    send_image,
)
from fm_comfyui_bridge.comfy_api import NEGATIVE
from fm_comfyui_bridge.lora_yaml import SdLoraYaml

SERVER_URL = None


def test_bridge_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    assert img is not None, "画像生成に失敗しました。"
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(path, upload_name="bridge_test.png", server_url=SERVER_URL)
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")


def test_bridge_highreso_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate_highreso(
        "1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL
    )
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(path, upload_name="bridge_test.png", server_url=SERVER_URL)
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")


def test_lora_yaml_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    # 読み込んだ lola ファイルの中身確認
    assert lora.lora_enabled, "lora enabled check failed"
    assert (
        lora.checkpoint == "catTowerNoobaiXL_v15Vpred.safetensors"
    ), "checkpoint check failed"
    assert lora.image_size == (1344, 768), "image size check failed"
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


def test_bridge_i2i_highreso():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    path1 = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path1), f"ファイルが存在しません: {path1}"
    #
    img = generate_i2i_highreso(
        "1girl", NEGATIVE, lora, lora.image_size, path1, server_url=SERVER_URL
    )
    path2 = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    #
    if os.path.exists(path1):
        os.remove(path1)
    if os.path.exists(path2):
        os.remove(path2)
        os.rmdir("./tests/outputs")


def test_bridge_free():
    response = free(server_url=SERVER_URL)
    assert (
        response.status_code == 200
    ), f"ステータスコードが不正です: {response.status_code}"


def test_bridge_list_models():
    folder = "checkpoints"
    response = list_models(folder, server_url=SERVER_URL)
    assert isinstance(response, list), f"レスポンスがリストではありません: {response}"
    assert len(response) > 0, f"モデルリストが空です: {response}"
    folder = "loras"
    response = list_models(folder, server_url=SERVER_URL)
    assert isinstance(response, list), f"レスポンスがリストではありません: {response}"
    assert len(response) > 0, f"モデルリストが空です: {response}"


def test_lora_yaml_sample_config():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    assert img is not None, "画像生成に失敗しました。"
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(path, upload_name="lora_yaml_sample_config.png", server_url=SERVER_URL)
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")


def test_lora_yaml_sample_config_modified():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    lora.data["sampling"]["steps"] = 20
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    assert img is not None, "画像生成に失敗しました。"
    lora.data["sampling"]["cfg"] = 7.0
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    assert img is not None, "画像生成に失敗しました。"
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(
        path, upload_name="lora_yaml_sample_config_modified.png", server_url=SERVER_URL
    )
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")


def test_lora_yaml_sample_config_without_samples():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    del lora.data["sampling"]
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    assert img is not None, "画像生成に失敗しました。"
    path = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path), f"ファイルが存在しません: {path}"
    send_image(
        path,
        upload_name="lora_yaml_sample_config_without_samples.png",
        server_url=SERVER_URL,
    )
    if os.path.exists(path):
        os.remove(path)  # yaml書き込み後、ファイル削除
        os.rmdir("./tests/outputs")
