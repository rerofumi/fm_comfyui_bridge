# fm_comfyui_bridge README


このプロジェクトは、[ComfyUI](https://github.com/comfyanonymous/ComfyUI) のAPIを通じて画像生成をプログラムから制御するためのPythonライブラリです。

主に、個人的なツール開発で ComfyUI の画像生成機能を再利用するために、共通処理を切り出したものになります。

## インストール

```bash
uv build
```

プロジェクトツールとして uv(astral-sh.uv) を使っています。`uv build` を実行すると、プロジェクトのビルドが行われ build ディレクトリに whl ファイルが作成されます。

この whl ファイルを別プロジェクトに `pip install` するなりして使用してください。


## 使い方

`fm_comfyui_bridge.bridge` 以下のメソッドを使用して、ComfyUI API とやり取りすることができます。

positive_prompt(text), negative_prompt(text), 出力モデル等の設定(SdLoraYaml) の 3つを渡すことで画像生成できることを目指しています。
テキストプロンプトや設定を、python コードで変更しながらバッチ出力するような小物ツールを作成できます。


### ComfyUI の準備

ローカル環境に ComfyUI のインストール、セットアップを行い動作している事を確認してください。

カスタムノードを使用しています。workflow ディレクトリにある `_API` が『付いていない』ワークフローを ComfyUI に読みこませて、全ノード問題なく動作することを確認してください。

以下のカスタムノードを使っています(できるだけ挙げましたが抜け漏れがあるかもしれません)

- ComfyUI_Comfyroll_CustomNodes
- ControlNet-LLLite-ComfyUI
  - tile model: bdsqlsz_controlllite_xl_tile_anime_beta.safetensors
  - tile model: bdsqlsz_controllite_xl_tile_anime_beta.safetensors

### API ドキュメント

#### `generate(prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]) -> Image`

指定されたプロンプトとパラメータを使用して画像を生成します。
ComfyUI のタスクキューが空になるまで待ちますので、他のタスク実行中だとなかなか戻ってこない事になります。
詳細はワークフローファイル `SDXL_LoRA_Base.json` を参照してください。

戻り値は PIL 形式のイメージです。

```
sample = api.generate(prompt="1girl", negative="low quality", lora=lora_yaml_instance, image_size=(1024, 1024))
```

#### `generate_highreso(prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]) -> Image`

マルチパスサンプリング＆アップスケールを使用します。時間はかかりますがちょっときれいな出力が得られます。
詳細はワークフローファイル `SDXL_HighReso.json` を参照してください。

```
sample = api.generate_highreso(prompt="1girl", negative="low quality", lora=lora_yaml_instance, image_size=(1024, 1024))
```

#### `generate_i2i_highreso(prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int], inputfile: str) -> Image`

マルチパスサンプリング＆アップスケールを使用した Image2Image を行います。
入力画像ファイルのパスを追加で与えてください。
入力画像はラフスケッチ程度に扱われプロンプトのほうが支配的です。
詳細はワークフローファイル `SDXL_HighReso_i2i.json` を参照してください。

```
sample = api.generate_i2i_highreso(prompt="1girl", negative="low quality", lora=lora_yaml_instance, image_size=(1024, 1024), "C:/input_image.png")
```

#### `save_image(image, posi=None, nega=None, filename=None, workspace=None, output_dir=None)`

PIL 形式の画像を保存します。
generate() で帰ってきた画像をファイルに保存するために使います。

posi, nega はテキストプロンプトを png の meta 情報として記録するためにつかわれます。指定無しでも構いません。

保存先のファイルパス、ファイル名は `workspace/output_dir/filename.png` という形になります。
workspace 未指定時の値はカレントディレクトリ、output_dir 未指定時の値は `outputs` です。

```
api.save_image(sample, posi="1girl", nega="low quality", filename="sample.png")
```

#### `free(server_url: str = None)`

モデルをアンロードし、メモリを解放します。

```
api.free()
```

#### `list_models(folder: str, server_url: str = None)`

指定されたフォルダ内のモデルのリストを取得します。

```
models = api.list_models(folder="checkpoints")
```

### SdLoraYaml クラス

`SdLoraYaml` クラスは、LoRAモデルの情報を保持し、YAMLファイルに読み書きするためのクラスです。

#### 読み書きメソッド

- `read_from_yaml(file_path: str)`: YAMLファイルからデータを読み込みます。
- `write_to_yaml(file_path: str = None)`: データをYAMLファイルに書き込みます。

#### プロパティ(読み出し)

- `lora_num`: LoRAモデル指定の数です。
- `lora_enabled_flag(index)`: 指定した番号のLoRAモデルの利用スイッチを返します。
- `lora_model(index)`: 指定した番号のLoRAモデルのファイル名を返します。
- `lora_trigger(index)`: 指定した番号のLoRAトリガーワードを返します。
- `lora_strength(index)`: 指定した番号のLoRAの強度を返します。
- `checkpoint`: SDXLチェックポイントモデルを返します。
- `image_size`: 出力イメージサイズを返します。
- `vpred`: Vpredモードフラグを返します。

プロパティへの書き込みは `SdLoraYaml.data` に対して直接行ってください。


### lora.yaml ファイル構造

`lora.yaml` ファイルは、`SdLoraYaml` クラスが読み込む設定ファイルで、このAPIにとって重要な設定です。
以下は、`lora.yaml` ファイルで使用されるキーの説明です。

- `checkpoint`: 使用するチェックポイントファイルの名前を指定します。
- `vpred`: 使うモデルが v-pred 仕様のときは true に設定します。
- `image-size`: 画像のサイズを指定します。
  - `width`: 画像の横幅サイズ
  - `height`: 画像の縦幅サイズ
- `lora`: LoRAモデルの設定を含むリストです。複数 LoRA の指定も省略することも可能です。
  - `enabled`: LoRAモデルの使用を有効または無効にします。
  - `model`: 使用するLoRAモデルのファイル名を指定します。
  - `strength`: LoRAの強度を指定します。
  - `trigger`: LoRAのトリガーワードを指定します。
- `sampling`: サンプリングパラメータを指定します。省略可。現在のところ HighReso モードでは無視されます。
  - `steps`: サンプリング数の指定
  - `cfg`: CFGスケール値の指定

## 変更履歴

### バージョン 0.9.0

- 複数 LoRA の指定が可能になった

### バージョン 0.8.4

- HighReso モードを改定、計算量を減らし元の絵を残すワークフローに変更

### バージョン 0.8.0

- lora.yaml でサンプリングパラメータを指定できるようにした

### バージョン 0.7.0

- free, list_models といった制御 API を追加

### バージョン 0.6.4

- bugfix

### バージョン 0.6.0

- バージョン更新、PyPI 登録

### バージョン 0.5.6

- ハイレゾ Workflow を用いた I2I generate を追加、パラメータ調整

### バージョン 0.5.3

- ハイレゾ Workflow 更新、パラメータ調整

### バージョン 0.5.0

- Workflow 刷新、lora 有り/無しと eps/vpred を 1つの workflow で表現
- マルチパスハイレゾモード追加(1.5倍にアップスケール)

### バージョン 0.4.0

- ComfyUI へ画像をアップロードする send_image() 関数を追加。I2I や mask 画像用


### バージョン 0.3.0

- README.md を追加
- ComfyUI API への接続先と画像の保存ディレクトリを指定できるようにした

### バージョン 0.1.0

- 初回リリース

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。

## 新モジュール: fm_comfy_request

`fm_comfy_request` は、任意の ComfyUI API workflow JSON を外部ファイルとして読み込み、workflow 内の `fm_comfy_request` meta ノードに書かれた YAML binding を使って生成リクエストを行う新しいインターフェースです。

旧 `fm_comfyui_bridge.bridge` はパッケージ同梱 workflow と固定 node ID を前提にしています。`fm_comfy_request` は他アプリから workflow を差し替えて使うことを想定し、生成結果を PIL ではなく PNG bytes として返します。これにより ComfyUI が出力した PNG metadata を保持できます。

### Workflow の配置

デフォルトでは以下のディレクトリから workflow JSON を読み込みます。

```text
~/.config/fm_comfy_request/workflow/
```

Windows でも `Path.home() / ".config" / "fm_comfy_request" / "workflow"` として解決されます。配置先は環境変数または引数で変更できます。

```powershell
$env:FM_COMFY_REQUEST_WORKFLOW_DIR = "E:\path\to\workflow"
$env:FM_COMFY_REQUEST_SERVER_URL = "http://127.0.0.1:8188/"
```

workflow 引数はファイル名、`.json` 省略名、または絶対パスを指定できます。

### Workflow meta YAML

workflow 内に `_meta.title` が `fm_comfy_request` の multiline text ノードを 1 つ置き、その本文に YAML を書きます。現在の実装では、各 binding は node ID または一意な `_meta.title` を文字列で指定します。

```yaml
model: "Load Checkpoint"
clip: "Load Checkpoint"
prompt: "Prompt"
negative-prompt: "Negative"
seed: "SamplerCustom"
seed-name: "noise_seed"
output: "Save Image"
input: "Load Image"
size: "Empty Latent Image"
sampling-mode: "ModelSamplingDiscrete"
steps: "BasicScheduler"
cfg: "SamplerCustom"
```

`model` は必須です。`clip` は clip 付き LoRA を使う場合に必要です。ただし `CheckpointLoaderSimple` のように `model` node から clip 出力を導出できる場合は省略できます。

`seed-name` を省略すると `noise_seed` を使います。対象 node に `noise_seed` がなく `seed` がある場合は `seed` にフォールバックします。

### CLI

基本形です。

```powershell
uv run fm-comfy-request workflow-list
uv run fm-comfy-request workflow-inspect SDXL_LoRA_Base.json
uv run fm-comfy-request generate SDXL_LoRA_Base.json --prompt "1girl, green hair" --output check.png
```

接続先や workflow ディレクトリを指定する場合は、サブコマンドより前にグローバルオプションを置きます。

```powershell
uv run fm-comfy-request --server-url http://127.0.0.1:8188/ --workflow-dir C:\Users\me\.config\fm_comfy_request\workflow generate SDXL_LoRA_Base.json --prompt "1girl" --output out.png
```

seed の扱いです。

```powershell
# seed 未指定: fm_comfy_request client が毎回ランダム seed を生成
uv run fm-comfy-request generate SDXL_LoRA_Base.json --prompt "1girl"

# 固定 seed
uv run fm-comfy-request generate SDXL_LoRA_Base.json --prompt "1girl" --seed 12345

# workflow JSON 内の seed をそのまま使う
uv run fm-comfy-request generate SDXL_LoRA_Base.json --prompt "1girl" --no-random-seed
```

I2I 生成です。workflow 側に `input` binding が必要です。

```powershell
uv run fm-comfy-request generate-i2i I2I_Workflow.json input.png --prompt "1girl" --seed 12345
```

モデル一覧とメモリ解放です。

```powershell
uv run fm-comfy-request models checkpoints
uv run fm-comfy-request models loras
uv run fm-comfy-request free
```

`generate --json` は `GenerationResult` の内容を JSON 形式で表示します。`workflow_final` や `history` も含むため、確認用途では出力が大きくなる場合があります。

現在の CLI では `--lora-yaml`, `--width`, `--height`, `--steps`, `--cfg`, `--timeout`, `--verbose` は未実装です。LoRA を使う場合は Python API から `ConfigLoraYaml` または `SdLoraYaml` を渡してください。

### Python 関数 API

他アプリから手軽に使う場合は、`fm_comfy_request` のトップレベル関数を import します。

```python
from pathlib import Path

from fm_comfy_request import generate

result = generate(
    "SDXL_LoRA_Base.json",
    prompt="1girl, green hair",
    negative="low quality, worst quality",
    server_url="http://127.0.0.1:8188/",
)

if result.images:
    Path("check.png").write_bytes(result.images[0].image_bytes)
```

固定 seed を使う場合です。

```python
from fm_comfy_request import generate

result = generate(
    "SDXL_LoRA_Base.json",
    prompt="1girl",
    seed=12345,
)
```

workflow 内の seed をそのまま使う場合です。

```python
from fm_comfy_request import generate

result = generate(
    "SDXL_LoRA_Base.json",
    prompt="1girl",
    random_seed=False,
)
```

I2I 生成です。

```python
from fm_comfy_request import generate_i2i

result = generate_i2i(
    "I2I_Workflow.json",
    "input.png",
    prompt="1girl",
)
```

非同期 API もあります。実装は同期 API を worker thread で実行します。

```python
import asyncio

from fm_comfy_request import generate_async

async def main():
    result = await generate_async("SDXL_LoRA_Base.json", prompt="1girl")
    return result

result = asyncio.run(main())
```

### Client API

同じ接続先や workflow ディレクトリを繰り返し使うアプリでは `ComfyRequestClient` を使います。

```python
from pathlib import Path

from fm_comfy_request.client import ComfyRequestClient

client = ComfyRequestClient(
    server_url="http://127.0.0.1:8188/",
    workflow_dir=Path.home() / ".config" / "fm_comfy_request" / "workflow",
    timeout_seconds=120,
)

result = client.generate("SDXL_LoRA_Base.json", prompt="1girl")
```

利用できる主なメソッドです。

- `generate(workflow, prompt=None, negative=None, lora=None, seed=None, random_seed=True, server_url=None, progress_callback=None)`
- `generate_i2i(workflow, input_image, prompt=None, negative=None, lora=None, seed=None, random_seed=True, server_url=None, progress_callback=None)`
- `inspect_workflow(workflow)`
- `list_workflows()`
- `list_models(folder, server_url=None)`
- `free(server_url=None)`

`seed=None` かつ `random_seed=True` で workflow に seed binding がある場合、client が `0` から `2**63 - 1` のランダム seed を生成して workflow に書き込みます。同じ prompt を連続実行しても ComfyUI のキャッシュで 0 秒完了しないようにするためです。

### LoRA 設定

`generate()` / `generate_i2i()` の `lora` には、既存の `SdLoraYaml` または新しい `ConfigLoraYaml` を渡せます。

```python
from fm_comfy_request import ConfigLoraYaml, generate

lora = ConfigLoraYaml()
lora.data = {
    "lora": [
        {
            "enabled": True,
            "model": "example.safetensors",
            "strength": 0.8,
            "model_only": False,
        }
    ]
}

result = generate("SDXL_LoRA_Base.json", prompt="1girl", lora=lora)
```

`model_only: true` の LoRA は `LoraLoaderModelOnly` として model のみに接続します。未指定または `false` の場合は `LoraLoader` として model と clip に接続します。

### 戻り値

`generate()` / `generate_i2i()` は `GenerationResult` を返します。

主なフィールドです。

- `prompt_id`: ComfyUI の prompt ID
- `client_id`: WebSocket 接続で使った client ID
- `workflow_path`: 読み込んだ workflow のパス
- `workflow_final`: prompt、seed、LoRA などを反映した最終 workflow
- `output_node_id`: 出力として参照した SaveImage node ID
- `images`: `GeneratedImage` のリスト
- `history`: ComfyUI の `/history/{prompt_id}` 応答

`GeneratedImage` の主なフィールドです。

- `filename`: ComfyUI 出力ファイル名
- `subfolder`: ComfyUI 出力サブフォルダ
- `type`: ComfyUI 出力 type
- `image_bytes`: PNG bytes

PIL に変換したい場合は `image_bytes_to_pil()` を使います。

```python
from fm_comfy_request import image_bytes_to_pil

image = image_bytes_to_pil(result.images[0].image_bytes)
```

bytes のまま保存する場合は PNG metadata を保持できます。

```python
from pathlib import Path

Path("output.png").write_bytes(result.images[0].image_bytes)
```

### 進捗コールバック

`progress_callback` を渡すと、WebSocket から受け取ったイベントを `ProgressEvent` として受け取れます。

```python
from fm_comfy_request import generate


def on_progress(event):
    if event.event_type == "progress":
        print(event.value, "/", event.max_value)


result = generate(
    "SDXL_LoRA_Base.json",
    prompt="1girl",
    progress_callback=on_progress,
)
```

### 例外

`fm_comfy_request` の例外は `FmComfyRequestError` を基底にしています。

```python
from fm_comfy_request import FmComfyRequestError, generate

try:
    result = generate("missing.json", prompt="1girl")
except FmComfyRequestError as exc:
    print(f"generation failed: {exc}")
```

代表的な例外です。

- `WorkflowNotFoundError`
- `WorkflowLoadError`
- `WorkflowMetaNotFoundError`
- `WorkflowMetaInvalidError`
- `NodeReferenceNotFoundError`
- `NodeReferenceAmbiguousError`
- `I2IUnsupportedError`
- `LoraClipOutputMissingError`
- `ComfyConnectionError`
- `ComfyRequestError`
- `ComfyTimeoutError`
- `ComfyExecutionError`