# fm_comfy_request 実装設計仕様

## 1. 本書の位置付け

本書は `plan/20260418/02_requirement.md` の機能要求を、現在の実装 (`src/fm_comfyui_bridge/bridge.py`、`config.py`、`lora_yaml.py`、`Workflow/*.json`) を踏まえて具体的な実装単位へ落とし込んだ設計仕様である。

本書では以下を定義する。

- 新モジュールの責務分割
- 公開 API と内部データモデル
- workflow 読み込み／検証／書き換え方式
- LoRA 動的挿入方式
- ComfyUI との通信方式
- CLI、例外、テスト、移行方針

コード断片は記載せず、実装判断に必要な粒度まで仕様を固定する。

## 2. 現行実装の整理

### 2.1 現状の構造

現行版は主に以下の構造で構成されている。

- `src/fm_comfyui_bridge/bridge.py`
  - ComfyUI への REST 通信
  - workflow JSON 読み込み
  - ノード値書き換え
  - LoRA ノード挿入
  - 画像保存
  - 公開関数 `generate`, `generate_highreso`, `generate_i2i_highreso`, `free`, `list_models`
- `src/fm_comfyui_bridge/config.py`
  - workflow ごとの固定ノード ID 定数
- `src/fm_comfyui_bridge/lora_yaml.py`
  - `SdLoraYaml` の YAML 入出力と既存設定アクセス
- `src/fm_comfyui_bridge/Workflow/*.json`
  - パッケージ同梱 workflow

### 2.2 現行実装の制約

新設計で解消すべき制約は以下である。

- workflow がパッケージ内部に固定され、任意 workflow を扱えない
- `config.py` の固定ノード ID に強く依存している
- `bridge.py` が通信・workflow 変換・画像処理を一体化しており責務分離が弱い
- 完了待機が `/queue` ポーリングであり、対象 prompt 単位ではなくサーバー全体キューの空きを見ている
- 戻り値が `PIL.Image` であり、ComfyUI 出力 PNG の meta を保持しづらい
- LoRA 挿入が checkpoint ノード前提で、`replace_value_recursive()` による全再帰置換に依存している
- テストが実 ComfyUI 依存の統合試験中心で、workflow 解析・LoRA 挿入の単体検証が薄い

### 2.3 設計上の重要な観察点

- 現行 workflow JSON では `_meta.title` が重複しうる。例として `SDXL_Base_API.json` では prompt 用と negative 用の両方が同一 title を持つ。
- 実際の workflow には `35:8` のような非純数値 node ID が含まれるため、node ID を整数限定では扱えない。
- `anima-base.json` のように `UNETLoader` と `CLIPLoader` が分離された workflow が存在するため、LoRA 用の clip ソースは model ソースから独立に指定できる必要がある。
- workflow 内に固定 LoRA ノードが既に含まれている場合があるため、LoRA-free な workflow を前提にした設計にはできない。
- meta 用 node として `PrimitiveStringMultiline` + `inputs.value` 形式が実例として存在する。
- 現行 workflow でも size, seed, sampling 関連の入力キー名は node class によって異なる。
- API JSON にはノードの出力スロット名は含まれないため、LoRA 挿入時に model/clip の出力位置を判断する仕組みが必要である。

## 3. 設計方針

### 3.1 基本方針

- 旧モジュールは原則変更しない。新機能は `fm_comfy_request` 独立トップレベルパッケージとして追加する。
- workflow は外部ファイルを読み込み、meta YAML を基準に動的に解釈する。
- 公開 API は同期／非同期の両方を提供する。
- workflow の書き換えは「構造化されたノード参照」と「入力名解決」を経て行い、固定 ID や全再帰文字列置換に頼らない。
- 画像はバイナリを正とし、PIL 変換は補助機能として分離する。
- 旧 API 互換性を壊さない。新旧どちらも同一配布パッケージから利用できる。

### 3.2 実装方針

- `src/fm_comfyui_bridge` 直下の既存モジュールは温存する。
- 新規ディレクトリ `src/fm_comfy_request/` を追加し、新 API をそこへ集約する。
- 同一配布パッケージ内に `fm_comfyui_bridge` と `fm_comfy_request` の 2 つのトップレベル Python パッケージを含める。
- `src/fm_comfy_request/__init__.py` を設け、公開 API の再エクスポートを行う。

## 4. モジュール構成

現在の実装で追加しているファイル構成を以下とする。

- `src/fm_comfy_request/__init__.py`
  - 公開関数、公開クラス、例外クラスのエクスポート
- `src/fm_comfy_request/api.py`
  - モジュールレベルの同期／非同期 convenience API
- `src/fm_comfy_request/client.py`
  - `ComfyRequestClient`（同期）
  - `AsyncComfyRequestClient`（非同期）
  - seed 未指定時のランダム seed 生成
- `src/fm_comfy_request/models.py`
  - dataclass / 型定義
- `src/fm_comfy_request/workflow.py`
  - workflow ファイル探索、パス解決、JSON 読み込み
  - meta ノード検出、YAML パース、正規化
  - node index 構築、ノード参照解決
  - パラメータ上書き、LoRA 挿入、I2I 検証
- `src/fm_comfy_request/transport.py`
  - REST / WebSocket 通信
- `src/fm_comfy_request/image_io.py`
  - bytes ↔ PIL 変換、保存処理
- `src/fm_comfy_request/exceptions.py`
  - 例外階層
- `src/fm_comfy_request/config_lora_yaml.py`
  - `ConfigLoraYaml`
- `src/fm_comfy_request/cli.py`
  - CLI 実装

当初設計で分割予定だった `workflow_store.py`, `workflow_meta.py`, `workflow_graph.py`, `workflow_mutator.py` は、現在の実装では `workflow.py` に集約している。

補助テストファイルとして現在追加しているものは以下である。

- `tests/unit/test_fm_comfy_request.py`
- `tests/unit/test_config_lora_yaml.py`

実 ComfyUI 依存のテストは既存 `tests/test_fm_comfyui_bridge.py` を環境変数で skip する形で維持している。
## 5. 公開 API 設計

### 5.1 公開の考え方

公開インターフェースは「関数 API」と「クライアント API」の 2 層にする。

- 軽量利用者向け: モジュールレベル関数
- 接続設定の再利用や将来拡張向け: クライアントクラス

### 5.2 モジュールレベル関数

以下を公開する。

- 通常生成（同期）
- 通常生成（非同期）
- I2I 生成（同期）
- I2I 生成（非同期）
- workflow 一覧取得
- workflow 解析／検証
- モデル一覧取得
- メモリ解放
- bytes → PIL 変換
- 画像保存

関数名は旧 API と衝突しないよう新トップレベルパッケージ内で次の命名を採用する。

- `generate`
- `generate_async`
- `generate_i2i`
- `generate_i2i_async`
- `list_workflows`
- `inspect_workflow`
- `list_models`
- `free`
- `image_bytes_to_pil`
- `save_image`

### 5.3 クライアントクラス

- `ComfyRequestClient`
  - サーバー URL
  - workflow ディレクトリ
  - タイムアウト
  - リトライ回数
  - ログ設定
  を保持する同期クライアント

- `AsyncComfyRequestClient`
  - 上記の非同期版

クライアントは stateful に設定を保持するが、workflow 自体は毎回 deep copy した上で処理し、内部キャッシュを外部へ露出させない。

## 6. 内部データモデル

以下の dataclass を `models.py` に定義する。

### 6.1 設定系

- `ClientSettings`
  - `server_url`
  - `workflow_dir`
  - `timeout_seconds`
  - `retry_count`
  - `retry_interval_seconds`
  - `connect_timeout_seconds`

- `GenerationOverrides`
  - `prompt`
  - `negative`
  - `seed`
  - `width`
  - `height`
  - `steps`
  - `cfg`
  - `sampling_mode`
  - `server_url`

### 6.2 workflow 系

- `NodeRef`
  - `node_id`
  - `title`
  - `class_type`
  - `input_name`
  - `model_output_index`
  - `clip_output_index`

- `WorkflowBindingSet`
  - `meta_node_id`
  - `model`
  - `clip`
  - `prompt`
  - `negative_prompt`
  - `seed`
  - `output`
  - `input`
  - `size`
  - `size_width`
  - `size_height`
  - `sampling_mode`
  - `steps`
  - `cfg`

- `LoadedWorkflow`
  - `path`
  - `raw_workflow`
  - `bindings`
  - `node_index_by_id`
  - `node_index_by_title`

### 6.3 結果系

- `GeneratedImage`
  - `filename`
  - `subfolder`
  - `type`
  - `image_bytes`

- `GenerationResult`
  - `prompt_id`
  - `client_id`
  - `workflow_path`
  - `workflow_final`
  - `output_node_id`
  - `images`
  - `history`

- `ProgressEvent`
  - `prompt_id`
  - `event_type`
  - `node_id`
  - `value`
  - `max_value`
  - `message`
  - `raw_event`

## 7. ConfigLoraYaml 設計

### 7.1 採用方針

- 新モジュールでは `ConfigLoraYaml` を採用する。
- `ConfigLoraYaml` は `fm_comfyui_bridge.lora_yaml.SdLoraYaml` の subclass とする。
- 旧 `SdLoraYaml` は原則無変更とし、旧 API 側への影響を避ける。

### 7.2 追加仕様

- `lora` 各要素について `model_only` を読み出す accessor を追加する
- 未記載時は `False` を返す
- 旧フォーマット YAML はそのまま読める
- 旧コードが新フォーマット YAML を読んでも extra field は無視される

### 7.3 新モジュール側の受け入れ方針

新 API は以下のいずれも受け入れる。

- `ConfigLoraYaml`
- 旧 `SdLoraYaml`
- `None`

旧 `SdLoraYaml` が渡された場合、`model_only` は常に `False` 扱いとする。

## 8. workflow ファイル解決設計

### 8.1 ディレクトリ解決

workflow ディレクトリは以下の優先順位で決定する。

1. 関数引数 / クライアント設定
2. 環境変数 `FM_COMFY_REQUEST_WORKFLOW_DIR`
3. `~/.config/fm_comfy_request/workflow/`

### 8.2 workflow パス解決

- 引数が絶対パスで存在すればそのまま使用する
- 相対名であれば workflow ディレクトリ配下を探索する
- 拡張子省略時は `.json` を補完して探索する
- 見つからない場合は `WorkflowNotFoundError`

### 8.3 読み込み

- JSON を辞書として読み込む
- top-level key は node ID 文字列であることを前提とし、`35:8` のような group 由来の ID も許容する
- node 定義は `inputs`, `class_type`, `_meta` を主に使用する

## 9. meta YAML 設計

### 9.1 meta ノード検出

workflow 内から `fm_comfy_request` meta ノードを 1 つだけ検出する。

検出条件は以下とする。

- `_meta.title == "fm_comfy_request"` を最優先
- `_meta` が無い場合のみ `title == "fm_comfy_request"` も許容

複数件検出時は `WorkflowMetaConflictError`、0件時は `WorkflowMetaNotFoundError` とする。

### 9.2 YAML 本文取得

meta ノード本文は node の `inputs` から次の優先順で取得する。

1. `text`
2. `value`
3. `string`

上記いずれにも文字列が無い場合は `WorkflowMetaInvalidError` とする。

### 9.3 YAML パース方針

- `yaml.safe_load()` で辞書へ変換する
- top-level が辞書でない場合はエラー
- 未知キーは現在の実装では保持されるが、binding 構築時に参照されない
- 既知 typo / alias は正規化する。現在の実装では warning ログは出していない
  - `samplingーmode` → `sampling-mode`
  - `negative_prompt` → 
egative-prompt`r

### 9.4 YAML の表現形式

現在の実装では、各 binding は短縮形の文字列のみを受け入れる。

- 文字列は node ID または unique title として扱う
- 詳細形マッピング（`id`, `title`, `class_type`, `input`, `model_output_index`, `clip_output_index` 等）は当初設計に含めていたが、現時点では未実装

### 9.5 ノード参照解決

文字列参照は以下の順で解決する。

1. node ID 完全一致
2. `_meta.title` 完全一致

現在の実装では title が複数ヒットする場合は `NodeReferenceAmbiguousError` とする。詳細形による曖昧性解消は未実装のため、重複 title がある場合は node ID を指定する。

### 9.6 入力名解決

現在の実装では binding 詳細形の `input` 指定は未実装であり、入力名は固定ルールで扱う。

- prompt / negative
  - `text` を更新する
  - `text_g`, `text_l` の同時更新は未実装
- seed
  - YAML 指定の `seed-name`
  - 未指定時は `noise_seed`
  - `seed-name` が未指定かつ対象 node に `noise_seed` がなく `seed` がある場合は `seed` にフォールバック
- size
  - `size` 指定時は `width` と `height`
  - `size-width` / `size-height` 指定時は `value`
- sampling_mode
  - `sampling`
- steps
  - `steps`
- cfg
  - `cfg`

入力名を解決できない場合の専用 `BindingInputNotFoundError` は定義済みだが、現在の実装では多くのケースで通常の辞書アクセス例外または node 参照例外として表面化する。

### 9.7 model / clip 出力スロット解決

LoRA 挿入用の source binding では出力スロットが必要になるため、現在の実装では class_type に基づく固定ルールを採用する。

- `model` binding の model 出力は常に slot `0`
- `clip` binding が明示される場合、clip 出力は既知 class_type から決定する
  - `CheckpointLoaderSimple` → `1`
  - `LoraLoader` → `1`
  - `CLIPLoader` → `0`
- `clip` binding が無い場合でも、`model` binding node が clip 出力を持つ既知 class_type なら `model` から clip 出力を自動補完する
- `UNETLoader`, `LoraLoaderModelOnly` 等の clip 非出力 node では clip 出力を自動補完しない
- `model_only = false` の LoRA が存在するのに、明示 `clip` binding と `model` 由来補完の両方が不可能な場合は `LoraClipOutputMissingError`

詳細形の `model_output_index` / `clip_output_index` 指定は当初設計に含めていたが、現在は未実装。

## 10. workflow 変換設計

### 10.1 処理順序

workflow 変換は以下の順で行う。

1. workflow 読み込み
2. meta YAML パース
3. binding 解決
4. request override 適用値の決定。seed 未指定かつ `random_seed=True` の場合は client がランダム seed を生成
5. workflow deep copy 作成
6. 通常パラメータ上書き
7. LoRA 挿入
8. 最終 validation

### 10.2 優先順位

上書き優先順位は以下とする。

1. API 引数の明示指定
2. seed 未指定かつ `random_seed=True` の場合に client が生成するランダム seed
3. workflow 既存値

`ConfigLoraYaml` 由来のサンプリング値上書きは当初設計に含めていたが、現在の実装では LoRA 挿入情報としてのみ使用している。

### 10.3 各パラメータの適用

- prompt
  - 対象 node の `text` 入力を書き換える
- negative
  - 対象 node の `text` 入力を書き換える
- seed
  - 明示指定時は固定値を書き込む
  - 未指定時は、seed binding があり `random_seed=True` なら `client.py` 内で `0` から `2**63 - 1` のランダム値を生成して書き込む
  - `random_seed=False` の場合は workflow 既存値を維持する
- size
  - 内部関数 `apply_overrides()` では単一 node 型または width/height 分離型の両方に対応する
  - 現在の public API / CLI からは未露出
- sampling_mode
  - 内部関数 `apply_overrides()` では `sampling` 入力を書き換える
  - 現在の public API / CLI からは未露出
- steps / cfg
  - 内部関数 `apply_overrides()` では値が与えられたときだけ更新する
  - 現在の public API / CLI からは未露出
### 10.4 link 走査方針

workflow 内リンクの置換は現在の実装では node 全体を再帰走査している。

置換対象は「長さ 2 の配列で、先頭が置換対象 node ID、後続が整数スロット」の形だけとする。文字列そのものは置換しないため、YAML 本文や通常テキストの node ID 文字列は置換されない。

## 11. LoRA 挿入設計

### 11.1 基本方式

- `model` binding が示す node を LoRA 挿入の起点とする
- clip 付き LoRA を使用する場合、`clip` binding が指定されていればそれを clip 起点とする。未指定時は `model` binding から clip 出力を導出できる場合に限りそれを使う
- enabled な LoRA を宣言順で順次挿入する
- 新 node ID は純数値の key を対象に最大値を求め、その +1 から連番付与する。純数値 key が存在しない場合は `1` から未使用の整数文字列を採用する

### 11.2 ノード生成

LoRA 1件ごとに以下を生成する。

- `model_only = false`
  - `class_type = "LoraLoader"`
  - inputs: `lora_name`, `strength_model`, `strength_clip`, `model`, `clip`
- `model_only = true`
  - `class_type = "LoraLoaderModelOnly"`
  - inputs: `lora_name`, `strength_model`, `model`

`trigger` は prompt 自動付加を行わず、設定情報として保持するのみとする。prompt への自動結合は要求に含めない。

### 11.3 再配線アルゴリズム

内部状態として以下を持つ。

- `current_model_source = (node_id, model_output_index)`
- `current_clip_source = (node_id, clip_output_index or None)`

`current_clip_source` は以下の優先順位で決定する。

1. 明示 `clip` binding
2. `model` binding node から導出できる clip 出力
3. `None`

LoRA 1件ごとに以下を行う。

1. 新 LoRA node を作成する
2. 新 node の model 入力を `current_model_source` に接続する
3. clip 付き LoRA の場合のみ、新 node の clip 入力を `current_clip_source` に接続する
4. workflow 全体の downstream 入力を走査し、旧 model source / clip source を参照するリンクだけを新 node 出力へ差し替える
5. `current_model_source` / `current_clip_source` を新 node 出力へ更新する

### 11.4 clip 不在時の扱い

- `model_only = false` の LoRA を使う際、明示 `clip` binding が無く、かつ `model` binding からも clip 出力が解決できなければエラー
- `model_only = true` だけが並ぶ場合、clip 解決は不要

### 11.5 現行実装との差分

現在の新モジュール実装では、旧 `replace_value_recursive()` と同様に node 全体を再帰走査する。ただし置換対象は ComfyUI のリンク形状である「長さ 2 の配列で、先頭が node ID、後続が整数スロット」の値に限定している。文字列値は置換しないため、YAML 本文や通常テキストの誤置換は避けられる。

### 11.6 既存固定 LoRA を含む workflow

- workflow 内に既存の `LoraLoader` / `LoraLoaderModelOnly` が含まれていても動作対象とする
- `model` / `clip` binding は loader ノードだけでなく、既存 LoRA ノード自体を起点として指定できる
- 再配線は binding が示す source を基準に行うため、「ベース workflow は LoRA を含まない」という前提を置かない

## 12. ComfyUI 通信設計

### 12.1 依存ライブラリ

新モジュールでは以下を採用する。

- HTTP: `httpx`
- WebSocket: `websockets`

旧モジュールは `requests` のまま維持する。

### 12.2 REST エンドポイント

使用する REST API は以下。

- `POST /prompt`
- `GET /history/{prompt_id}`
- `GET /view`
- `POST /upload/image`
- `POST /free`
- `GET /models/{folder}`

### 12.3 WebSocket エンドポイント

- `GET /ws?clientId=<client_id>`

通信手順は以下とする。

1. `client_id` を生成する
2. WebSocket 接続を確立する
3. `POST /prompt` に workflow と `client_id` を送る
4. 受信イベントを `prompt_id` 単位でフィルタする
5. 完了イベント受信後に `GET /history/{prompt_id}` を取得する
6. 対象出力画像を `GET /view` で取得する

この方式により、他ジョブ実行中でも「自分の prompt 完了」を判定できる。

### 12.4 進捗イベント

WebSocket から受けたイベントは `ProgressEvent` に正規化し、コールバックへ渡す。

コールバック仕様は以下。

- 同期 API: 通常関数を受け取る
- 非同期 API: 通常関数または awaitable を返す関数を受け取れる

### 12.5 タイムアウト・リトライ

- 現在の実装では `ClientSettings.timeout_seconds` を REST リクエスト、WebSocket 接続、進捗待機に共通利用する。
- `ClientSettings` には `retry_count`, `retry_interval_seconds`, `connect_timeout_seconds` が存在するが、現在の `Transport` では自動リトライと接続タイムアウト分離は未実装。
- `POST /prompt` の自動再送は二重投入リスクがあるため行わない。

## 13. 画像入出力設計

### 13.1 生成結果の保持

生成画像は `GeneratedImage.image_bytes` に raw bytes として保持する。

### 13.2 PIL 変換

- `image_bytes_to_pil()` で必要時のみ `PIL.Image` へ変換する
- 変換は読み取り専用補助とし、通常フローでは bytes を維持する

### 13.3 保存

`save_image()` は入力型に応じて動作を分ける。

- bytes 入力
  - raw bytes をそのまま保存する
  - PNG meta を保持する
- PIL 入力
  - PIL で保存する

デフォルト保存先は旧 API に合わせて `outputs/` とするが、新版では workspace / output_dir を `pathlib.Path` 基準で扱う。

### 13.4 upload_image

I2I 用画像アップロードでは、現行 `send_image()` のような RGBA 再エンコードは行わず、元ファイル bytes または入力 bytes をそのまま送る。

## 14. 生成結果設計

### 14.1 複数画像対応

ComfyUI の `SaveImage` は複数画像を返す場合があるため、戻り値は単一画像ではなく `GeneratedImage` の配列を正とする。

### 14.2 convenience

利用者の簡便性のため、先頭画像を主結果として扱う補助プロパティまたは helper を設けることは許容するが、内部表現は配列とする。

### 14.3 返却内容

最低限以下を返す。

- `prompt_id`
- `client_id`
- 最終 workflow
- 取得した history
- 出力 node ID
- 画像配列

## 15. CLI 設計

### 15.1 コマンド名

`pyproject.toml` の `[project.scripts]` に次を登録する。

- `fm-comfy-request`

### 15.2 サブコマンド

現在の CLI サブコマンドは以下である。

- `workflow-list`
  - workflow ディレクトリ内一覧
- `workflow-inspect`
  - meta YAML と binding 解決結果の表示
- `generate`
  - 通常生成
- `generate-i2i`
  - I2I 生成
- `models`
  - 指定フォルダのモデル一覧表示
- `free`
  - メモリ解放要求

当初案の `workflow list` / `workflow inspect` という階層型サブコマンドではなく、現在は `workflow-list` / `workflow-inspect` として実装している。

### 15.3 主要オプション

現在実装済みの主要オプションは以下である。

- グローバル
  - `--workflow-dir`
  - `--server-url`
- `generate`
  - positional `workflow`
  - `--prompt`
  - `--negative`
  - `--seed`
  - `--no-random-seed`
  - `--output`
  - `--json`
- `generate-i2i`
  - positional `workflow`
  - positional `input_image`
  - `--prompt`
  - `--negative`
  - `--seed`
  - `--no-random-seed`
- `models`
  - positional `folder`

`--lora-yaml`, `--width`, `--height`, `--steps`, `--cfg`, `--timeout`, `--verbose` は当初案に含めていたが、現在の CLI では未実装。

### 15.4 実装方針

- 依存追加を最小にするため `argparse` を採用する
- CLI 本体は薄く保ち、内部では `api.py` を呼び出すだけにする
- seed の乱数生成は CLI では行わず、`seed` と `random_seed` 指定を client に渡す
- エラー時は human-readable なメッセージを stderr に出す
- `--verbose` と traceback 表示切替は現在未実装

## 16. 例外設計

`exceptions.py` に以下の階層を定義する。

- `FmComfyRequestError`
  - `WorkflowNotFoundError`
  - `WorkflowLoadError`
  - `WorkflowMetaNotFoundError`
  - `WorkflowMetaConflictError`
  - `WorkflowMetaInvalidError`
  - `NodeReferenceError`
    - `NodeReferenceAmbiguousError`
    - `NodeReferenceNotFoundError`
  - `BindingInputNotFoundError`
  - `WorkflowValidationError`
  - `I2IUnsupportedError`
  - `LoraInsertionError`
    - `LoraClipOutputMissingError`
  - `ComfyConnectionError`
  - `ComfyRequestError`
  - `ComfyTimeoutError`
  - `ComfyExecutionError`

例外メッセージには以下を含める。

- workflow path
- 対象 binding 名
- 対象 node id / title
- 失敗した endpoint または event 種別

## 17. テスト設計

### 17.1 単体テスト

単体テストはネットワーク非依存とし、以下を検証する。

- workflow path 解決
- meta YAML パース
- alias / typo 正規化
- node 参照解決
- `35:8` のような mixed node ID の解決
- title 重複時エラー
- input 名自動解決
- size 単一 node / 分離 node 処理
- model / clip 分離 workflow の clip source 解決
- LoRA model_only / clip 付き挿入
- 既存固定 LoRA を含む workflow への追加挿入
- 複数 LoRA 時の source 更新
- `ConfigLoraYaml` の後方互換

### 17.2 統合テスト

統合テストは `pytest.mark.integration` を付け、ComfyUI 起動環境でのみ走るものに分離する。

統合テストでは以下を確認する。

- 通常生成
- I2I 生成
- 進捗イベント受信
- bytes 保存時の PNG 保持
- モデル一覧取得
- メモリ解放

### 17.3 テストデータ

現在の単体テストでは、必要な minimal workflow をテスト内で辞書または一時 JSON として構築している。`tests/data/` 配下の固定テストデータは現時点では未追加。
## 18. ドキュメント更新設計

- `README.md` に新モジュール章を追加する
- 旧 API と新 API の違いを比較表ではなく箇条書きで明示する
- workflow 配置方法
- meta YAML の短縮形（詳細形は未実装）
- `ConfigLoraYaml` の新項目
- CLI 使用例

を追加する。

## 19. 実装順序

現在の実装は以下のまとまりで追加されている。

1. `exceptions.py`, `models.py`, `config_lora_yaml.py`
2. `workflow.py`
3. `transport.py`
4. `client.py`, `api.py`
5. `image_io.py`
6. `cli.py`
7. 単体テスト
8. README 更新

当初案の `workflow_store.py`, `workflow_meta.py`, `workflow_graph.py`, `workflow_mutator.py` への分割は行わず、`workflow.py` に集約している。

## 20. 旧実装との共存方針

- `bridge.py`, `config.py`, `lora_yaml.py`, `Workflow/` は当面維持する
- 旧 API の挙動変更は本件では行わない
- 新モジュールから旧 `SdLoraYaml` を受け入れることで、既存の設定資産を流用可能にする
- 同一 wheel に `fm_comfyui_bridge` と `fm_comfy_request` を同梱し、利用者はどちらか一方を選択して import できるようにする
- package version は 0.10 系として新機能追加版に位置づける

## 21. 設計上の確定事項

本設計で確定する事項は以下である。

- 新版は `fm_comfy_request` 独立トップレベルパッケージとして追加する
- workflow は外部 JSON + meta YAML で解決する
- node ID は純数値に限定せず扱う
- node 参照は title だけでなく node ID も正式対応とする
- YAML は現在、短縮形の文字列 binding を許容する。詳細形は未実装
- clip source は model source と独立に指定できる
- LoRA 挿入は model source を起点にした構造的再配線で行う
- clip 出力は自動判定できない場合に明示指定を許容する
- 完了待機は WebSocket + prompt_id フィルタで行う
- 戻り値は画像 bytes の配列を基本とする
- CLI は `argparse` で実装する
- 旧 API は残し、新 API は別モジュールで提供する
