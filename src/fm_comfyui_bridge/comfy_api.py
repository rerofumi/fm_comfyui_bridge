NEGATIVE = """
((worst quality, low quality)), normal quality, ((poorly drawn face)), poorly drawn hands, ugly, bad anatomy, (bad hands), (missing fingers), disfigured, mutation, mutated, (extra limb),missing limbs, floating limbs, disconnected limbs, signature, watermark, username, blurry, cropped
"""

WORKFLOW = "Workflow"

NORMAL_WORKFLOW = """
{
  "4": {
    "inputs": {
      "ckpt_name": "catTowerNoobaiXL_v15Vpred.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "6": {
    "inputs": {
      "text": "masterpiece, best quality, newest, absurdres, highres, 1girl",
      "speak_and_recognation": true,
      "clip": [
        "19",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "7": {
    "inputs": {
      "text": "worst quality, old, early, low quality, lowres, signature, username, logo, bad hands, mutated hands, mammal, anthro, furry, ambiguous form, feral, semi-anthro, 3d, 3dcg, parker, hood",
      "speak_and_recognation": true,
      "clip": [
        "19",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "10",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "10": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 954711114757980,
      "cfg": 5,
      "model": [
        "16",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "sampler": [
        "11",
        0
      ],
      "sigmas": [
        "12",
        0
      ],
      "latent_image": [
        "15",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "11": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "12": {
    "inputs": {
      "scheduler": "normal",
      "steps": 24,
      "denoise": 0.98,
      "model": [
        "16",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "15": {
    "inputs": {
      "width": 1344,
      "height": 768,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "16": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "19",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "19": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "4",
        0
      ],
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "26": {
    "inputs": {
      "filename_prefix": "2025-01-01/Bridge",
      "images": [
        "8",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  }
}
"""


HIGHRES_WORKFLOW = """
{
  "1": {
    "inputs": {
      "text": "tillhi, masterpiece, best quality, 1girl, waitress, cafe bar, frill skirt, disher",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "🔤 CR Text"
    }
  },
  "2": {
    "inputs": {
      "text": "worst quality, old, early, low quality, lowres, signature, username, logo, bad hands, mutated hands, mammal, anthro, furry, ambiguous form, feral, semi-anthro, 3d, 3dcg",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "🔤 CR Text"
    }
  },
  "5": {
    "inputs": {
      "ckpt_name": "catTowerNoobaiXL_v15Vpred.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "7": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 0.6,
      "strength_clip": 0.6,
      "model": [
        "12",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "12": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "13": {
    "inputs": {
      "scheduler": "normal",
      "steps": 10,
      "denoise": 1,
      "model": [
        "12",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "19": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "20": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 173407566755529,
      "cfg": 7,
      "model": [
        "7",
        0
      ],
      "positive": [
        "152",
        0
      ],
      "negative": [
        "153",
        0
      ],
      "sampler": [
        "19",
        0
      ],
      "sigmas": [
        "13",
        0
      ],
      "latent_image": [
        "166",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "31": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "32": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 0.8,
      "strength_clip": 0.8,
      "model": [
        "31",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "35": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "36": {
    "inputs": {
      "scheduler": "simple",
      "steps": 8,
      "denoise": 0.85,
      "model": [
        "31",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "37": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 95099951283096,
      "cfg": 5,
      "model": [
        "32",
        0
      ],
      "positive": [
        "154",
        0
      ],
      "negative": [
        "155",
        0
      ],
      "sampler": [
        "35",
        0
      ],
      "sigmas": [
        "36",
        0
      ],
      "latent_image": [
        "122",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "43": {
    "inputs": {
      "samples": [
        "20",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "44": {
    "inputs": {
      "images": [
        "121",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "45": {
    "inputs": {
      "samples": [
        "37",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "47": {
    "inputs": {
      "images": [
        "45",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "48": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "51": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "53": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 1069930693430089,
      "cfg": 3,
      "model": [
        "54",
        0
      ],
      "positive": [
        "156",
        0
      ],
      "negative": [
        "157",
        0
      ],
      "sampler": [
        "51",
        0
      ],
      "sigmas": [
        "55",
        0
      ],
      "latent_image": [
        "37",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "54": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 0.9,
      "strength_clip": 0.9,
      "model": [
        "48",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "55": {
    "inputs": {
      "scheduler": "simple",
      "steps": 12,
      "denoise": 0.7000000000000001,
      "model": [
        "48",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "56": {
    "inputs": {
      "images": [
        "57",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "57": {
    "inputs": {
      "samples": [
        "53",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "65": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "67": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "68",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "68": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "69": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 842504059028136,
      "cfg": 3,
      "model": [
        "67",
        0
      ],
      "positive": [
        "158",
        0
      ],
      "negative": [
        "159",
        0
      ],
      "sampler": [
        "65",
        0
      ],
      "sigmas": [
        "70",
        0
      ],
      "latent_image": [
        "53",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "70": {
    "inputs": {
      "scheduler": "simple",
      "steps": 24,
      "denoise": 0.6,
      "model": [
        "68",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "72": {
    "inputs": {
      "samples": [
        "69",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "73": {
    "inputs": {
      "images": [
        "72",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "80": {
    "inputs": {
      "sampler_name": "euler_ancestral"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "82": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "83",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "83": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "84": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 346794832178234,
      "cfg": 3,
      "model": [
        "101",
        0
      ],
      "positive": [
        "160",
        0
      ],
      "negative": [
        "161",
        0
      ],
      "sampler": [
        "80",
        0
      ],
      "sigmas": [
        "85",
        0
      ],
      "latent_image": [
        "173",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "85": {
    "inputs": {
      "scheduler": "simple",
      "steps": 36,
      "denoise": 0.5,
      "model": [
        "101",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "93": {
    "inputs": {
      "samples": [
        "84",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "94": {
    "inputs": {
      "images": [
        "93",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "99": {
    "inputs": {
      "samples": [
        "173",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "101": {
    "inputs": {
      "model_name": "bdsqlsz_controlllite_xl_tile_anime_beta.safetensors",
      "strength": 0.85,
      "steps": 36,
      "start_percent": 0,
      "end_percent": 80,
      "model": [
        "82",
        0
      ],
      "cond_image": [
        "99",
        0
      ]
    },
    "class_type": "LLLiteLoader",
    "_meta": {
      "title": "Load LLLite"
    }
  },
  "111": {
    "inputs": {
      "filename_prefix": "2025-01-04/HighRes",
      "images": [
        "148",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "121": {
    "inputs": {
      "strength": 0.5,
      "mode": "white",
      "tint_color_hex": "#000000",
      "image": [
        "43",
        0
      ]
    },
    "class_type": "CR Color Tint",
    "_meta": {
      "title": "🎨 CR Color Tint"
    }
  },
  "122": {
    "inputs": {
      "pixels": [
        "121",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "128": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 79419633471033,
      "cfg": 3,
      "model": [
        "137",
        0
      ],
      "positive": [
        "162",
        0
      ],
      "negative": [
        "163",
        0
      ],
      "sampler": [
        "136",
        0
      ],
      "sigmas": [
        "135",
        0
      ],
      "latent_image": [
        "177",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "133": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "138",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "134": {
    "inputs": {
      "samples": [
        "177",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "135": {
    "inputs": {
      "scheduler": "simple",
      "steps": 36,
      "denoise": 0.2,
      "model": [
        "137",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "136": {
    "inputs": {
      "sampler_name": "euler_ancestral"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "137": {
    "inputs": {
      "model_name": "bdsqlsz_controlllite_xl_tile_anime_beta.safetensors",
      "strength": 1,
      "steps": 36,
      "start_percent": 0,
      "end_percent": 100,
      "model": [
        "133",
        0
      ],
      "cond_image": [
        "134",
        0
      ]
    },
    "class_type": "LLLiteLoader",
    "_meta": {
      "title": "Load LLLite"
    }
  },
  "138": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "142": {
    "inputs": {
      "integer": [
        "164",
        1
      ],
      "multiple": 2
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "147": {
    "inputs": {
      "integer": [
        "165",
        1
      ],
      "multiple": 2
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "148": {
    "inputs": {
      "samples": [
        "128",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "149": {
    "inputs": {
      "images": [
        "148",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "152": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "7",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "153": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "7",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "154": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "155": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "156": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "54",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "157": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "54",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "158": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "67",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "159": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "67",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "160": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "82",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "161": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "82",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "162": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "133",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "163": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "133",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "164": {
    "inputs": {
      "value": 1344
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "BaseSize-Width"
    }
  },
  "165": {
    "inputs": {
      "value": 768
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "BaseSize-Height"
    }
  },
  "166": {
    "inputs": {
      "width": [
        "164",
        1
      ],
      "height": [
        "165",
        1
      ],
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "167": {
    "inputs": {
      "samples": [
        "69",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "168": {
    "inputs": {
      "upscale_method": "lanczos",
      "width": [
        "169",
        0
      ],
      "height": [
        "170",
        0
      ],
      "crop": "disabled",
      "image": [
        "167",
        0
      ]
    },
    "class_type": "ImageScale",
    "_meta": {
      "title": "Upscale Image"
    }
  },
  "169": {
    "inputs": {
      "integer": [
        "164",
        1
      ],
      "multiple": 1.5
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "170": {
    "inputs": {
      "integer": [
        "165",
        1
      ],
      "multiple": 1.5
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "173": {
    "inputs": {
      "pixels": [
        "168",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "175": {
    "inputs": {
      "upscale_method": "lanczos",
      "width": [
        "142",
        0
      ],
      "height": [
        "147",
        0
      ],
      "crop": "disabled",
      "image": [
        "176",
        0
      ]
    },
    "class_type": "ImageScale",
    "_meta": {
      "title": "Upscale Image"
    }
  },
  "176": {
    "inputs": {
      "samples": [
        "84",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "177": {
    "inputs": {
      "pixels": [
        "175",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  }
}
"""

HIGHRES_I2I_WORKFLOW = """
{
  "1": {
    "inputs": {
      "text": "tillhi, masterpiece, best quality, 1girl, waitress, cafe bar, frill skirt, disher",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "🔤 CR Text"
    }
  },
  "2": {
    "inputs": {
      "text": "worst quality, old, early, low quality, lowres, signature, username, logo, bad hands, mutated hands, mammal, anthro, furry, ambiguous form, feral, semi-anthro, 3d, 3dcg",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "🔤 CR Text"
    }
  },
  "5": {
    "inputs": {
      "ckpt_name": "catTowerNoobaiXL_v15Vpred.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "7": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 0.6,
      "strength_clip": 0.6,
      "model": [
        "12",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "12": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "13": {
    "inputs": {
      "scheduler": "simple",
      "steps": 8,
      "denoise": 0.7000000000000001,
      "model": [
        "12",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "19": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "20": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 942231486746652,
      "cfg": 7,
      "model": [
        "7",
        0
      ],
      "positive": [
        "152",
        0
      ],
      "negative": [
        "153",
        0
      ],
      "sampler": [
        "19",
        0
      ],
      "sigmas": [
        "13",
        0
      ],
      "latent_image": [
        "125",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "31": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "32": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 0.8,
      "strength_clip": 0.8,
      "model": [
        "31",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "35": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "36": {
    "inputs": {
      "scheduler": "simple",
      "steps": 10,
      "denoise": 0.8,
      "model": [
        "31",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "37": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 6078924935363,
      "cfg": 5,
      "model": [
        "32",
        0
      ],
      "positive": [
        "154",
        0
      ],
      "negative": [
        "155",
        0
      ],
      "sampler": [
        "35",
        0
      ],
      "sigmas": [
        "36",
        0
      ],
      "latent_image": [
        "122",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "43": {
    "inputs": {
      "samples": [
        "20",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "44": {
    "inputs": {
      "images": [
        "121",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "45": {
    "inputs": {
      "samples": [
        "37",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "47": {
    "inputs": {
      "images": [
        "45",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "48": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "51": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "53": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 511133294639095,
      "cfg": 3,
      "model": [
        "54",
        0
      ],
      "positive": [
        "156",
        0
      ],
      "negative": [
        "157",
        0
      ],
      "sampler": [
        "51",
        0
      ],
      "sigmas": [
        "55",
        0
      ],
      "latent_image": [
        "37",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "54": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 0.9,
      "strength_clip": 0.9,
      "model": [
        "48",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "55": {
    "inputs": {
      "scheduler": "simple",
      "steps": 12,
      "denoise": 0.65,
      "model": [
        "48",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "56": {
    "inputs": {
      "images": [
        "57",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "57": {
    "inputs": {
      "samples": [
        "53",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "65": {
    "inputs": {
      "sampler_name": "euler"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "67": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "68",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "68": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "69": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 955774721657174,
      "cfg": 3,
      "model": [
        "67",
        0
      ],
      "positive": [
        "158",
        0
      ],
      "negative": [
        "159",
        0
      ],
      "sampler": [
        "65",
        0
      ],
      "sigmas": [
        "70",
        0
      ],
      "latent_image": [
        "53",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "70": {
    "inputs": {
      "scheduler": "simple",
      "steps": 24,
      "denoise": 0.6,
      "model": [
        "68",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "72": {
    "inputs": {
      "samples": [
        "69",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "73": {
    "inputs": {
      "images": [
        "72",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "80": {
    "inputs": {
      "sampler_name": "euler_ancestral"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "82": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "83",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "83": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "84": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 229634304802029,
      "cfg": 3,
      "model": [
        "101",
        0
      ],
      "positive": [
        "160",
        0
      ],
      "negative": [
        "161",
        0
      ],
      "sampler": [
        "80",
        0
      ],
      "sigmas": [
        "85",
        0
      ],
      "latent_image": [
        "172",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "85": {
    "inputs": {
      "scheduler": "simple",
      "steps": 36,
      "denoise": 0.5,
      "model": [
        "101",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "93": {
    "inputs": {
      "samples": [
        "84",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "94": {
    "inputs": {
      "images": [
        "93",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "99": {
    "inputs": {
      "samples": [
        "172",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "101": {
    "inputs": {
      "model_name": "bdsqlsz_controlllite_xl_tile_anime_beta.safetensors",
      "strength": 0.85,
      "steps": 36,
      "start_percent": 0,
      "end_percent": 80,
      "model": [
        "82",
        0
      ],
      "cond_image": [
        "99",
        0
      ]
    },
    "class_type": "LLLiteLoader",
    "_meta": {
      "title": "Load LLLite"
    }
  },
  "111": {
    "inputs": {
      "filename_prefix": "2025-01-04/HighRes",
      "images": [
        "148",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "121": {
    "inputs": {
      "strength": 0.5,
      "mode": "white",
      "tint_color_hex": "#000000",
      "image": [
        "43",
        0
      ]
    },
    "class_type": "CR Color Tint",
    "_meta": {
      "title": "🎨 CR Color Tint"
    }
  },
  "122": {
    "inputs": {
      "pixels": [
        "121",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "123": {
    "inputs": {
      "image": "Bridge_00002_.png",
      "upload": "image"
    },
    "class_type": "LoadImage",
    "_meta": {
      "title": "Load Image"
    }
  },
  "124": {
    "inputs": {
      "pixels": [
        "123",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "125": {
    "inputs": {
      "upscale_method": "bilinear",
      "width": [
        "164",
        1
      ],
      "height": [
        "165",
        1
      ],
      "crop": "center",
      "samples": [
        "124",
        0
      ]
    },
    "class_type": "LatentUpscale",
    "_meta": {
      "title": "Upscale Latent"
    }
  },
  "126": {
    "inputs": {
      "samples": [
        "125",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "127": {
    "inputs": {
      "images": [
        "126",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "128": {
    "inputs": {
      "add_noise": true,
      "noise_seed": 54659552276610,
      "cfg": 3,
      "model": [
        "137",
        0
      ],
      "positive": [
        "162",
        0
      ],
      "negative": [
        "163",
        0
      ],
      "sampler": [
        "136",
        0
      ],
      "sigmas": [
        "135",
        0
      ],
      "latent_image": [
        "177",
        0
      ]
    },
    "class_type": "SamplerCustom",
    "_meta": {
      "title": "SamplerCustom"
    }
  },
  "133": {
    "inputs": {
      "lora_name": "lora-ix-tillhi-v1.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "138",
        0
      ],
      "clip": [
        "5",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  },
  "134": {
    "inputs": {
      "samples": [
        "177",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "135": {
    "inputs": {
      "scheduler": "simple",
      "steps": 36,
      "denoise": 0.2,
      "model": [
        "137",
        0
      ]
    },
    "class_type": "BasicScheduler",
    "_meta": {
      "title": "BasicScheduler"
    }
  },
  "136": {
    "inputs": {
      "sampler_name": "euler_ancestral"
    },
    "class_type": "KSamplerSelect",
    "_meta": {
      "title": "KSamplerSelect"
    }
  },
  "137": {
    "inputs": {
      "model_name": "bdsqlsz_controlllite_xl_tile_anime_beta.safetensors",
      "strength": 1,
      "steps": 36,
      "start_percent": 0,
      "end_percent": 100,
      "model": [
        "133",
        0
      ],
      "cond_image": [
        "134",
        0
      ]
    },
    "class_type": "LLLiteLoader",
    "_meta": {
      "title": "Load LLLite"
    }
  },
  "138": {
    "inputs": {
      "sampling": "v_prediction",
      "zsnr": false,
      "model": [
        "5",
        0
      ]
    },
    "class_type": "ModelSamplingDiscrete",
    "_meta": {
      "title": "ModelSamplingDiscrete"
    }
  },
  "142": {
    "inputs": {
      "integer": [
        "164",
        1
      ],
      "multiple": 2
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "147": {
    "inputs": {
      "integer": [
        "165",
        1
      ],
      "multiple": 2
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "148": {
    "inputs": {
      "samples": [
        "128",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "149": {
    "inputs": {
      "images": [
        "148",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "152": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "7",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "153": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "7",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "154": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "155": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "156": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "54",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "157": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "54",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "158": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "67",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "159": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "67",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "160": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "82",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "161": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "82",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "162": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "133",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "163": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "speak_and_recognation": true,
      "clip": [
        "133",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode (Prompt)"
    }
  },
  "164": {
    "inputs": {
      "value": 1344
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "BaseSize-Width"
    }
  },
  "165": {
    "inputs": {
      "value": 768
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "BaseSize-Height"
    }
  },
  "168": {
    "inputs": {
      "integer": [
        "164",
        1
      ],
      "multiple": 1.5
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "169": {
    "inputs": {
      "integer": [
        "165",
        1
      ],
      "multiple": 1.5
    },
    "class_type": "CR Integer Multiple",
    "_meta": {
      "title": "⚙️ CR Integer Multiple"
    }
  },
  "170": {
    "inputs": {
      "upscale_method": "lanczos",
      "width": [
        "168",
        0
      ],
      "height": [
        "169",
        0
      ],
      "crop": "disabled",
      "image": [
        "171",
        0
      ]
    },
    "class_type": "ImageScale",
    "_meta": {
      "title": "Upscale Image"
    }
  },
  "171": {
    "inputs": {
      "samples": [
        "69",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "172": {
    "inputs": {
      "pixels": [
        "170",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  },
  "175": {
    "inputs": {
      "upscale_method": "lanczos",
      "width": [
        "142",
        0
      ],
      "height": [
        "147",
        0
      ],
      "crop": "disabled",
      "image": [
        "176",
        0
      ]
    },
    "class_type": "ImageScale",
    "_meta": {
      "title": "Upscale Image"
    }
  },
  "176": {
    "inputs": {
      "samples": [
        "84",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "177": {
    "inputs": {
      "pixels": [
        "175",
        0
      ],
      "vae": [
        "5",
        2
      ]
    },
    "class_type": "VAEEncode",
    "_meta": {
      "title": "VAE Encode"
    }
  }
}
"""
