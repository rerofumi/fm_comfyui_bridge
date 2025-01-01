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
      "text": "masterpiece, best quality, 1girl",
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
      "strength_model": 0.5,
      "strength_clip": 0.5,
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
  "10": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "7",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "11": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "7",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
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
      "steps": 6,
      "denoise": 0.9500000000000001,
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
  "18": {
    "inputs": {
      "width": [
        "115",
        1
      ],
      "height": [
        "116",
        1
      ],
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
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
      "noise_seed": 267154279535817,
      "cfg": 7,
      "model": [
        "7",
        0
      ],
      "positive": [
        "10",
        0
      ],
      "negative": [
        "11",
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
        "18",
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
  "33": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "34": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "32",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
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
      "steps": 6,
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
      "noise_seed": 810346326537406,
      "cfg": 5,
      "model": [
        "32",
        0
      ],
      "positive": [
        "33",
        0
      ],
      "negative": [
        "34",
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
        "20",
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
        "43",
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
  "49": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "54",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "50": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "54",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
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
      "noise_seed": 1107390956268487,
      "cfg": 3,
      "model": [
        "54",
        0
      ],
      "positive": [
        "49",
        0
      ],
      "negative": [
        "50",
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
      "denoise": 0.8,
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
  "63": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "67",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "64": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "67",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
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
      "noise_seed": 442188505345866,
      "cfg": 3,
      "model": [
        "67",
        0
      ],
      "positive": [
        "63",
        0
      ],
      "negative": [
        "64",
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
      "denoise": 0.65,
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
  "78": {
    "inputs": {
      "text": [
        "1",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "82",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "79": {
    "inputs": {
      "text": [
        "2",
        0
      ],
      "parser": "A1111",
      "mean_normalization": true,
      "multi_conditioning": false,
      "use_old_emphasis_implementation": false,
      "with_SDXL": false,
      "ascore": 6,
      "width": 1024,
      "height": 1024,
      "crop_w": 0,
      "crop_h": 0,
      "target_width": 1024,
      "target_height": 1024,
      "text_g": "",
      "text_l": "",
      "smZ_steps": 1,
      "speak_and_recognation": true,
      "clip": [
        "82",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
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
      "noise_seed": 691435221795426,
      "cfg": 3,
      "model": [
        "101",
        0
      ],
      "positive": [
        "78",
        0
      ],
      "negative": [
        "79",
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
        "90",
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
  "90": {
    "inputs": {
      "upscale_method": "bicubic",
      "scale_by": [
        "114",
        0
      ],
      "samples": [
        "69",
        0
      ]
    },
    "class_type": "LatentUpscaleBy",
    "_meta": {
      "title": "Upscale Latent By"
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
        "90",
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
      "strength": 0.7000000000000001,
      "steps": 36,
      "start_percent": 15,
      "end_percent": 90,
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
      "filename_prefix": "2025-01-01/HighRes",
      "images": [
        "93",
        0
      ]
    },
    "class_type": "SaveImage",
    "_meta": {
      "title": "Save Image"
    }
  },
  "114": {
    "inputs": {
      "value": 1.5
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "⚙️Upscale Ratio"
    }
  },
  "115": {
    "inputs": {
      "value": 1344
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "Base Width"
    }
  },
  "116": {
    "inputs": {
      "value": 768
    },
    "class_type": "CR Value",
    "_meta": {
      "title": "Base Height"
    }
  }
}
"""
