from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, PngImagePlugin


def image_bytes_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def save_image(image, posi=None, nega=None, filename=None, workspace=None, output_dir=None):
    workspace = Path(workspace or ".")
    output_dir = Path(output_dir or "outputs")
    output_dir = workspace / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    if filename is None:
        filename = "image.png"
    path = output_dir / filename
    if isinstance(image, (bytes, bytearray)):
        path.write_bytes(bytes(image))
        return path
    if posi is not None or nega is not None:
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("parameters", f"{posi}\nNegative prompt: {nega}\n")
        image.save(path, "PNG", pnginfo=metadata)
    else:
        image.save(path)
    return path
