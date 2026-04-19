from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .api import free, generate, generate_i2i, inspect_workflow, list_models, list_workflows
from .exceptions import FmComfyRequestError



def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fm-comfy-request")
    parser.add_argument("--workflow-dir", default=None)
    parser.add_argument("--server-url", default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("workflow-list")
    inspect = sub.add_parser("workflow-inspect")
    inspect.add_argument("workflow")
    gen = sub.add_parser("generate")
    gen.add_argument("workflow")
    gen.add_argument("--prompt")
    gen.add_argument("--negative")
    gen.add_argument("--model")
    gen.add_argument("--seed", type=int)
    gen.add_argument("--denoise", type=float)
    gen.add_argument("--no-random-seed", action="store_true", help="use the seed stored in the workflow")
    gen.add_argument("--output")
    gen.add_argument("--json", action="store_true")
    i2i = sub.add_parser("generate-i2i")
    i2i.add_argument("workflow")
    i2i.add_argument("input_image")
    i2i.add_argument("--prompt")
    i2i.add_argument("--negative")
    i2i.add_argument("--model")
    i2i.add_argument("--seed", type=int)
    i2i.add_argument("--denoise", type=float)
    i2i.add_argument("--no-random-seed", action="store_true", help="use the seed stored in the workflow")
    i2i.add_argument("--output")
    models = sub.add_parser("models")
    models.add_argument("folder")
    sub.add_parser("free")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.cmd == "workflow-list":
            for path in list_workflows(workflow_dir=args.workflow_dir):
                print(path)
        elif args.cmd == "workflow-inspect":
            print(json.dumps(inspect_workflow(args.workflow, workflow_dir=args.workflow_dir), ensure_ascii=False, default=str, indent=2))
        elif args.cmd == "generate":
            result = generate(args.workflow, model=args.model, prompt=args.prompt, negative=args.negative, seed=args.seed, random_seed=not args.no_random_seed, denoise=args.denoise, server_url=args.server_url, workflow_dir=args.workflow_dir)
            if args.output and result.images:
                Path(args.output).write_bytes(result.images[0].image_bytes)
            if args.json:
                print(json.dumps(asdict(result), ensure_ascii=False, default=str, indent=2))
        elif args.cmd == "generate-i2i":
            result = generate_i2i(args.workflow, args.input_image, model=args.model, prompt=args.prompt, negative=args.negative, seed=args.seed, random_seed=not args.no_random_seed, denoise=args.denoise, server_url=args.server_url, workflow_dir=args.workflow_dir)
            if args.output and result.images:
                Path(args.output).write_bytes(result.images[0].image_bytes)
            print(json.dumps(asdict(result), ensure_ascii=False, default=str, indent=2))
        elif args.cmd == "models":
            print(json.dumps(list_models(args.folder, server_url=args.server_url, workflow_dir=args.workflow_dir), ensure_ascii=False, default=str, indent=2))
        elif args.cmd == "free":
            print(json.dumps(free(server_url=args.server_url, workflow_dir=args.workflow_dir), ensure_ascii=False, default=str, indent=2))
        return 0
    except FmComfyRequestError as exc:
        print(str(exc), file=sys.stderr)
        return 1
