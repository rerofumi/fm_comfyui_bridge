NEGATIVE = """
((worst quality, low quality)), normal quality, ((poorly drawn face)), poorly drawn hands, ugly, bad anatomy, (bad hands), (missing fingers), disfigured, mutation, mutated, (extra limb),missing limbs, floating limbs, disconnected limbs, signature, watermark, username, blurry, cropped
"""


API_NO_LORA = """
{
  "1": {
    "inputs": {
      "ckpt_name": "model.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "2": {
    "inputs": {
      "text": [
        "3",
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
        "1",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "3": {
    "inputs": {
      "text": "1girl",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "Positive Prompt"
    }
  },
  "4": {
    "inputs": {
      "text": "((worst quality, low quality)), normal quality, ((poorly drawn face)), poorly drawn hands, ugly, bad anatomy, (bad hands), (missing fingers), disfigured, mutation, mutated, (extra limb),missing limbs, floating limbs, disconnected limbs, signature, watermark, username, blurry, cropped",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "Negative Prompt"
    }
  },
  "5": {
    "inputs": {
      "text": [
        "4",
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
        "1",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "7": {
    "inputs": {
      "seed": 422927919864905,
      "steps": 20,
      "cfg": 7,
      "sampler_name": "euler_ancestral",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "1",
        0
      ],
      "positive": [
        "2",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "9",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "9": {
    "inputs": {
      "width": [
        "14",
        0
      ],
      "height": [
        "15",
        0
      ],
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "10": {
    "inputs": {
      "samples": [
        "7",
        0
      ],
      "vae": [
        "1",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "12": {
    "inputs": {
      "filename": "Easy_%time_%counter",
      "path": "%date/",
      "seed": 0,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler_ancestral",
      "scheduler": "normal",
      "width": [
        "14",
        0
      ],
      "height": [
        "15",
        0
      ],
      "positive": [
        "3",
        0
      ],
      "negative": [
        "4",
        0
      ],
      "extension": "png",
      "calculate_hash": true,
      "resource_hash": true,
      "lossless_webp": true,
      "jpg_webp_quality": 100,
      "date_format": "%Y-%m-%d",
      "time_format": "%H%M%S",
      "save_metadata_file": false,
      "extra_info": "",
      "speak_and_recognation": true,
      "images": [
        "10",
        0
      ]
    },
    "class_type": "SDPromptSaver",
    "_meta": {
      "title": "SD Prompt Saver"
    }
  },
  "14": {
    "inputs": {
      "int": 1024
    },
    "class_type": "Primitive integer [Crystools]",
    "_meta": {
      "title": "🪛 Image Width"
    }
  },
  "15": {
    "inputs": {
      "int": 1024
    },
    "class_type": "Primitive integer [Crystools]",
    "_meta": {
      "title": "Image Height"
    }
  }
}
"""


API_WITH_LORA = """
{
  "1": {
    "inputs": {
      "ckpt_name": "model.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "Load Checkpoint"
    }
  },
  "2": {
    "inputs": {
      "text": [
        "3",
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
        "16",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "3": {
    "inputs": {
      "text": "1girl",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "Positive Prompt"
    }
  },
  "4": {
    "inputs": {
      "text": "((worst quality, low quality)), normal quality, ((poorly drawn face)), poorly drawn hands, ugly, bad anatomy, (bad hands), (missing fingers), disfigured, mutation, mutated, (extra limb),missing limbs, floating limbs, disconnected limbs, signature, watermark, username, blurry, cropped",
      "speak_and_recognation": true
    },
    "class_type": "CR Text",
    "_meta": {
      "title": "Negative Prompt"
    }
  },
  "5": {
    "inputs": {
      "text": [
        "4",
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
        "16",
        1
      ]
    },
    "class_type": "smZ CLIPTextEncode",
    "_meta": {
      "title": "CLIP Text Encode++"
    }
  },
  "7": {
    "inputs": {
      "seed": 422927919864905,
      "steps": 20,
      "cfg": 7,
      "sampler_name": "euler_ancestral",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "16",
        0
      ],
      "positive": [
        "2",
        0
      ],
      "negative": [
        "5",
        0
      ],
      "latent_image": [
        "9",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "KSampler"
    }
  },
  "9": {
    "inputs": {
      "width": [
        "14",
        0
      ],
      "height": [
        "15",
        0
      ],
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "Empty Latent Image"
    }
  },
  "10": {
    "inputs": {
      "samples": [
        "7",
        0
      ],
      "vae": [
        "1",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAE Decode"
    }
  },
  "12": {
    "inputs": {
      "filename": "Easy_%time_%counter",
      "path": "%date/",
      "seed": 0,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler_ancestral",
      "scheduler": "normal",
      "width": [
        "14",
        0
      ],
      "height": [
        "15",
        0
      ],
      "positive": [
        "3",
        0
      ],
      "negative": [
        "4",
        0
      ],
      "extension": "png",
      "calculate_hash": true,
      "resource_hash": true,
      "lossless_webp": true,
      "jpg_webp_quality": 100,
      "date_format": "%Y-%m-%d",
      "time_format": "%H%M%S",
      "save_metadata_file": false,
      "extra_info": "",
      "speak_and_recognation": true,
      "images": [
        "10",
        0
      ]
    },
    "class_type": "SDPromptSaver",
    "_meta": {
      "title": "SD Prompt Saver"
    }
  },
  "14": {
    "inputs": {
      "int": 1024
    },
    "class_type": "Primitive integer [Crystools]",
    "_meta": {
      "title": "🪛 Image Width"
    }
  },
  "15": {
    "inputs": {
      "int": 1024
    },
    "class_type": "Primitive integer [Crystools]",
    "_meta": {
      "title": "Image Height"
    }
  },
  "16": {
    "inputs": {
      "lora_name": "lora.safetensors",
      "strength_model": 1,
      "strength_clip": 1,
      "model": [
        "1",
        0
      ],
      "clip": [
        "1",
        1
      ]
    },
    "class_type": "LoraLoader",
    "_meta": {
      "title": "Load LoRA"
    }
  }
}
"""
