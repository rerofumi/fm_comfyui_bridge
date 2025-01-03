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

`fm_comfui_bridge.bridge` 以下のメソッドを使用して、ComfyUI API とやり取りすることができます。

positive_prompt(text), negative_prompt(text), 出力モデル等の設定(SdLoraYaml) の 3つを渡すことで画像生成できることを目指しています。
テキストプロンプトや設定を、python コードで変更しながらバッチ出力するような小物ツールを作成できます。


### ComfyUI の準備

ローカル環境に ComfyUI のインストール、セットアップを行い動作している事を確認してください。

カスタムノードを使用しています。workflow ディレクトリにある `_api` が『付いていない』ワークフローを ComfyUI に読みこませて、全ノード問題なく動作することを確認してください。

以下のカスタムノードを使っています(できるだけ挙げましたが抜け漏れがあるかもしれません)

- ComfyUI_Comfyroll_CustomNodes
- ControlNet-LLLite-ComfyUI
  - tile model: bdsqlsz_controlllite_xl_tile_anime_beta.safetensors


### API ドキュメント

#### `generate(prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]) -> Image`

指定されたプロンプトとパラメータを使用して画像を生成します。
ComfyUI のタスクキューが空になるまで待ちますので、他のタスク実行中だとなかなか戻ってこない事になります。

戻り値は PIL 形式のイメージです。

```
sample = api.generate(prompt="1girl", negative="low quality", lora=lora_yaml_instance, image_size=(1024, 1024))
```

#### `generate_highreso(prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int]) -> Image`

マルチパスサンプリング＆アップスケールを使用します。時間はかかりますがちょっときれいな出力が得られます。
詳細はワークフローファイル `MultiPassSampling.json` を参照してください。

```
sample = api.generate_highreso(prompt="1girl", negative="low quality", lora=lora_yaml_instance, image_size=(1024, 1024))
```

#### `generate_i2i_highreso(prompt: str, negative: str, lora: SdLoraYaml, image_size: tuple[int, int], inputfile: str) -> Image`

マルチパスサンプリング＆アップスケールを使用した Image2Image を行います。
入力画像ファイルのパスを追加で与えてください。
入力画像はラフスケッチ程度に扱われプロンプトのほうが支配的です。
詳細はワークフローファイル `MultiPassSampling_i2i.json` を参照してください。

```
sample = api.generate_i2i_highreso(prompt="1girl", negative="low quality", lora=lora_yaml_instance, image_size=(1024, 1024), "C:/input_image.png")
```


#### `save_image(image, posi=None, nega=None, filename=None, workspace=None, output_dir=None)`

PIL 形式の画像を保存します。
generate() で帰ってきた画像をファイルに保存するために使います。

post, nega はテキストプロンプトを png の meta 情報として記録するためにつかわれます。指定無しでも構いません。

保存先のファイルパス、ファイル名は `workspace/output_dir/filename.png` という形になります。
workspace 未指定時の値はカレントディレクトリ、output_dir 未指定時の値は `outputs` です。

```
save_image(sample, posi="1girl", nega="low quality", filename="sample.png")
```


### SdLoraYaml クラス

`SdLoraYaml` クラスは、LoRAモデルの情報を保持し、YAMLファイルに読み書きするためのクラスです。

#### 読み書きメソッド

- `read_from_yaml(file_path: str)`: YAMLファイルからデータを読み込みます。
- `write_to_yaml(file_path: str = None)`: データをYAMLファイルに書き込みます。

#### プロパティ(読み出し)

- `lora_enabled`: LoRAモデルの利用スイッチを返します。
- `model`: LoRAモデルのファイル名を返します。
- `trigger`: LoRAトリガーワードを返します。
- `strength`: LoRAの強度を返します。
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
- `lora`: LoRAモデルの設定を含むリストです。複数 LoRA の指定を意図してリストになっていますが現在は先頭の 1つしか使いません。
  - `model`: 使用するLoRAモデルのファイル名を指定します。LoRA disable 時でも model は必要です、存在するファイルを指定してください。
  - `enabled`: LoRAモデルの使用を有効または無効にします。
  - `strength`: LoRAの強度を指定します。
  - `trigger`: LoRAのトリガーワードを指定します。

## 変更履歴

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
