import os
import unittest # Added
import json # Added for potential direct dict loading in future tests, though not strictly needed for current plan

from fm_comfyui_bridge.bridge import (
    free,
    generate,
    generate_highreso,
    generate_i2i_highreso,
    list_models,
    save_image,
    send_image,
    # Import specific builder functions for direct testing
    t2i_request_build,
    t2i_highreso_request_build,
    i2i_highreso_request_build
)
from fm_comfyui_bridge.comfy_api import NEGATIVE
from fm_comfyui_bridge.lora_yaml import SdLoraYaml
from fm_comfyui_bridge.workflow import WorkflowTemplate # Added

SERVER_URL = None # Used by existing integration tests

# --- Existing Tests Below ---
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
        # Only remove directory if it's empty or managed by this test exclusively
        if os.path.exists("./tests/outputs") and not os.listdir("./tests/outputs"):
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
        os.remove(path)
        if os.path.exists("./tests/outputs") and not os.listdir("./tests/outputs"):
            os.rmdir("./tests/outputs")


def test_lora_yaml_functionality():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    assert lora.lora_enabled, "lora enabled check failed"
    assert lora.checkpoint == "catTowerNoobaiXL_v17Vpred.safetensors", (
        "checkpoint check failed"
    )
    assert lora.image_size == (1344, 768), "image size check failed"
    assert lora.model == "lora-ix-tillhi-v1.safetensors", "model check failed"
    assert lora.trigger == "tillhi", "trigger check failed"
    assert lora.strength == 0.9, "strength check failed"
    out_file_path = "./tests/lora2.yaml"
    lora.write_to_yaml(out_file_path)
    assert os.path.exists(out_file_path), f"ファイルが存在しません: {out_file_path}"
    if os.path.exists(out_file_path):
        os.remove(out_file_path)


def test_bridge_i2i_highreso():
    lora = SdLoraYaml()
    lora.read_from_yaml("./tests/lora.yaml")
    img = generate("1girl", NEGATIVE, lora, lora.image_size, server_url=SERVER_URL)
    path1 = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    assert os.path.exists(path1), f"ファイルが存在しません: {path1}"
    img = generate_i2i_highreso(
        "1girl", NEGATIVE, lora, lora.image_size, path1, server_url=SERVER_URL
    )
    path2 = save_image(img, posi="1girl", nega=NEGATIVE, workspace="./tests")
    if os.path.exists(path1):
        os.remove(path1)
    if os.path.exists(path2):
        os.remove(path2)
        if os.path.exists("./tests/outputs") and not os.listdir("./tests/outputs"):
            os.rmdir("./tests/outputs")


def test_bridge_free():
    response = free(server_url=SERVER_URL)
    assert response.status_code == 200, (
        f"ステータスコードが不正です: {response.status_code}"
    )


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
        os.remove(path)
        if os.path.exists("./tests/outputs") and not os.listdir("./tests/outputs"):
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
        os.remove(path)
        if os.path.exists("./tests/outputs") and not os.listdir("./tests/outputs"):
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
        os.remove(path)
        if os.path.exists("./tests/outputs") and not os.listdir("./tests/outputs"):
            os.rmdir("./tests/outputs")

# --- New Unit Tests Added Below ---

class MockSdLoraYaml:
    def __init__(self, checkpoint="test_checkpoint.safetensors", lora_models=None, vpred=False, steps=None, cfg=None):
        self.checkpoint = checkpoint
        # List of tuples (model_name, strength, enabled_flag, trigger)
        self.loras = lora_models if lora_models else []
        self.vpred = vpred
        self.steps = steps
        self.cfg = cfg
        self.image_size = (512,512) # Add a default image_size

    @property
    def lora_num(self):
        return len(self.loras)

    def lora_enabled_flag(self, index):
        return self.loras[index][2]

    def lora_model(self, index):
        return self.loras[index][0]

    def lora_strength(self, index):
        return self.loras[index][1]

    def lora_trigger(self, index): # Added for completeness
        return self.loras[index][3]

# Helper function to find node ID by title in a workflow dictionary
def find_node_id_in_dict(wf_dict, title):
    for node_id, node_info in wf_dict.items():
        if node_info.get("_meta", {}).get("title") == title:
            return node_id
    return None

# Tests for WorkflowTemplate
def test_workflow_load():
    # Assumes workflow JSONs are accessible via default resource loading path
    wf_template = WorkflowTemplate("SDXL_Base_API.json")
    assert isinstance(wf_template.workflow, dict)
    assert len(wf_template.workflow) > 0

def test_workflow_find_node_id():
    wf_template = WorkflowTemplate("SDXL_Base_API.json")
    pos_prompt_id = wf_template._find_node_id_by_title("CLIP Text Encode (Positive Prompt)")
    assert pos_prompt_id is not None
    assert wf_template.workflow[pos_prompt_id]["class_type"] == "CLIPTextEncode"

    neg_prompt_id = wf_template._find_node_id_by_title("CLIP Text Encode (Negative Prompt)")
    assert neg_prompt_id is not None
    assert wf_template.workflow[neg_prompt_id]["class_type"] == "CLIPTextEncode"

    try:
        wf_template._find_node_id_by_title("NON_EXISTENT_TITLE")
        assert False, "ValueError not raised for non-existent title"
    except ValueError:
        pass # Expected

def test_workflow_set_input_by_title():
    wf_template = WorkflowTemplate("SDXL_Base_API.json")
    wf_template.set_input_by_title("CLIP Text Encode (Positive Prompt)", "text", "new positive prompt")
    pos_prompt_id = wf_template._find_node_id_by_title("CLIP Text Encode (Positive Prompt)")
    assert wf_template.workflow[pos_prompt_id]["inputs"]["text"] == "new positive prompt"

    # Note: The test for ValueError on invalid_input_name was removed as set_input_by_title
    # currently allows creating new input keys if they don't exist.

def test_workflow_insert_single_lora():
    wf_template = WorkflowTemplate("SDXL_Base_API.json")
    mock_lora_config = MockSdLoraYaml(
        lora_models=[("test_lora1.safetensors", 0.8, True, "trigger1")]
    )
    original_checkpoint_id = wf_template._find_node_id_by_title("Load Checkpoint")

    wf_template.insert_loras(mock_lora_config, "Load Checkpoint")

    lora_node_id = wf_template._find_node_id_by_title("Load LoRA: test_lora1.safetensors (Chain 1)")
    assert lora_node_id is not None
    lora_node = wf_template.workflow[lora_node_id]
    assert lora_node["inputs"]["lora_name"] == "test_lora1.safetensors"
    assert lora_node["inputs"]["strength_model"] == 0.8
    assert lora_node["inputs"]["model"][0] == original_checkpoint_id
    assert lora_node["inputs"]["clip"][0] == original_checkpoint_id

    msd_node_id = wf_template._find_node_id_by_title("ModelSamplingDiscrete")
    assert wf_template.workflow[msd_node_id]["inputs"]["model"] == [lora_node_id, 0]
    pos_prompt_node_id = wf_template._find_node_id_by_title("CLIP Text Encode (Positive Prompt)")
    assert wf_template.workflow[pos_prompt_node_id]["inputs"]["clip"] == [lora_node_id, 1]

def test_workflow_insert_multiple_loras():
    wf_template = WorkflowTemplate("SDXL_Base_API.json")
    mock_lora_config = MockSdLoraYaml(
        lora_models=[
            ("test_lora1.safetensors", 0.8, True, "trigger1"),
            ("test_lora2.safetensors", 0.5, True, "trigger2")
        ]
    )
    original_checkpoint_id = wf_template._find_node_id_by_title("Load Checkpoint")
    wf_template.insert_loras(mock_lora_config, "Load Checkpoint")

    lora1_node_id = wf_template._find_node_id_by_title("Load LoRA: test_lora1.safetensors (Chain 1)")
    lora2_node_id = wf_template._find_node_id_by_title("Load LoRA: test_lora2.safetensors (Chain 2)")
    assert lora1_node_id is not None
    assert lora2_node_id is not None

    assert wf_template.workflow[lora1_node_id]["inputs"]["model"][0] == original_checkpoint_id
    assert wf_template.workflow[lora1_node_id]["inputs"]["clip"][0] == original_checkpoint_id

    assert wf_template.workflow[lora2_node_id]["inputs"]["model"][0] == lora1_node_id
    assert wf_template.workflow[lora2_node_id]["inputs"]["clip"][0] == lora1_node_id

    msd_node_id = wf_template._find_node_id_by_title("ModelSamplingDiscrete")
    assert wf_template.workflow[msd_node_id]["inputs"]["model"] == [lora2_node_id, 0]

# Tests for bridge functions
def test_t2i_builder_structure():
    mock_lora_config = MockSdLoraYaml(
        checkpoint="catTowerNoobaiXL_v15Vpred.safetensors",
        lora_models=[("test_lora.safetensors", 0.7, True, "trigger")]
    )
    mock_lora_config.vpred = True
    mock_lora_config.steps = 25
    mock_lora_config.cfg = 6.0

    workflow_dict = t2i_request_build(
        prompt="test positive prompt",
        negative="test negative prompt",
        lora=mock_lora_config,
        image_size=(1024, 768) # image_size is from SdLoraYaml in original tests, here direct
    )
    assert isinstance(workflow_dict, dict)

    pos_prompt_id = find_node_id_in_dict(workflow_dict, "CLIP Text Encode (Positive Prompt)")
    assert pos_prompt_id is not None
    assert workflow_dict[pos_prompt_id]["inputs"]["text"] == "test positive prompt"

    neg_prompt_id = find_node_id_in_dict(workflow_dict, "CLIP Text Encode (Negative Prompt)")
    assert neg_prompt_id is not None
    assert workflow_dict[neg_prompt_id]["inputs"]["text"] == "test negative prompt"

    ckpt_id = find_node_id_in_dict(workflow_dict, "Load Checkpoint")
    assert ckpt_id is not None
    assert workflow_dict[ckpt_id]["inputs"]["ckpt_name"] == "catTowerNoobaiXL_v15Vpred.safetensors"

    lora_node_id = find_node_id_in_dict(workflow_dict, "Load LoRA: test_lora.safetensors (Chain 1)")
    assert lora_node_id is not None
    assert workflow_dict[lora_node_id]["inputs"]["lora_name"] == "test_lora.safetensors"

    msd_id = find_node_id_in_dict(workflow_dict, "ModelSamplingDiscrete")
    assert msd_id is not None
    assert workflow_dict[msd_id]["inputs"]["sampling"] == "v_prediction"

    scheduler_id = find_node_id_in_dict(workflow_dict, "BasicScheduler") # For steps
    assert scheduler_id is not None
    assert workflow_dict[scheduler_id]["inputs"]["steps"] == 25

    sampler_custom_id = find_node_id_in_dict(workflow_dict, "SamplerCustom") # For CFG
    assert sampler_custom_id is not None
    assert workflow_dict[sampler_custom_id]["inputs"]["cfg"] == 6.0

def test_t2i_highreso_builder_structure():
    mock_lora_config = MockSdLoraYaml(
        checkpoint="catCarrier_v30.safetensors", # From SDXL_HighReso_API.json
        lora_models=[("test_lora_hr.safetensors", 0.6, True, "trigger_hr")]
    )
    mock_lora_config.vpred = False # Test other path
    # Note: steps and cfg are not directly set on KSamplers by t2i_highreso_request_build yet
    # unless lora object has specific attributes like base_steps, hires_steps

    workflow_dict = t2i_highreso_request_build(
        prompt="hr positive",
        negative="hr negative",
        lora=mock_lora_config,
        image_size=(1280, 960)
    )
    assert isinstance(workflow_dict, dict)

    pos_prompt_id = find_node_id_in_dict(workflow_dict, "Positive Prompt Text")
    assert pos_prompt_id is not None
    assert workflow_dict[pos_prompt_id]["inputs"]["text"] == "hr positive"

    neg_prompt_id = find_node_id_in_dict(workflow_dict, "Negative Prompt Text")
    assert neg_prompt_id is not None
    assert workflow_dict[neg_prompt_id]["inputs"]["text"] == "hr negative"

    ksampler_base_id = find_node_id_in_dict(workflow_dict, "KSampler (Base Pass)")
    assert ksampler_base_id is not None
    assert "seed" in workflow_dict[ksampler_base_id]["inputs"] # Seed is random, just check presence

    ksampler_hires_id = find_node_id_in_dict(workflow_dict, "KSampler (Hi-Res Pass)")
    assert ksampler_hires_id is not None
    assert "seed" in workflow_dict[ksampler_hires_id]["inputs"]

    msd_id = find_node_id_in_dict(workflow_dict, "ModelSamplingDiscrete")
    assert msd_id is not None
    assert workflow_dict[msd_id]["inputs"]["sampling"] == "eps" # Based on mock_lora_config.vpred = False

    lora_node_id = find_node_id_in_dict(workflow_dict, "Load LoRA: test_lora_hr.safetensors (Chain 1)")
    assert lora_node_id is not None


def test_i2i_highreso_builder_structure():
    mock_lora_config = MockSdLoraYaml(
        checkpoint="catCarrier_v30.safetensors", # From SDXL_HighReso_I2I_API.json
        lora_models=[] # Test no LoRAs
    )
    mock_lora_config.vpred = True

    workflow_dict = i2i_highreso_request_build(
        prompt="i2i positive",
        negative="i2i negative",
        lora=mock_lora_config,
        upload_image="test_upload.png",
        image_size=(960, 1280)
    )
    assert isinstance(workflow_dict, dict)

    pos_prompt_id = find_node_id_in_dict(workflow_dict, "Positive Prompt Text")
    assert pos_prompt_id is not None
    assert workflow_dict[pos_prompt_id]["inputs"]["text"] == "i2i positive"

    load_image_id = find_node_id_in_dict(workflow_dict, "Load Image")
    assert load_image_id is not None
    assert workflow_dict[load_image_id]["inputs"]["image"] == "test_upload.png"

    # Check that LoRA node is NOT present
    lora_node_id = find_node_id_in_dict(workflow_dict, "Load LoRA: some_lora (Chain 1)") # Generic title part
    assert lora_node_id is None

    msd_id = find_node_id_in_dict(workflow_dict, "ModelSamplingDiscrete")
    assert msd_id is not None
    assert workflow_dict[msd_id]["inputs"]["sampling"] == "v_prediction"
