# fm_comfy_request 機能要求仕様

## 1. 本書の位置付け

`01_claim.md` に記載された要望を基に、新モジュール `fm_comfy_request` の機能要求を整理・拡張したものである。本書は機能要求（何ができるべきか）に焦点を当てており、実装方式やクラス構造・コード例は次工程（設計書）で扱う。

## 2. 目的とスコープ

### 2.1 目的
- 現行 `fm_comfyui_bridge` モジュール（以下「旧モジュール」）の利用範囲を広げるため、より汎用的に ComfyUI workflow を扱える新モジュール `fm_comfy_request` を提供する。
- 旧モジュールでは workflow がパッケージ内に固定されており、任意 workflow への差し替えが困難だった制約を解消する。
- LoRA ノードの挿入対象や対象ノード（特に CLIP の有無）を workflow 側の意図に従って選択できるようにする。

### 2.2 スコープ
- 本件で追加するのは `fm_comfy_request` サブパッケージ、および CLI コマンドである。
- 旧モジュール（`fm_comfyui_bridge.bridge`、`fm_comfyui_bridge.lora_yaml` 等）の機能・互換性は維持する。

### 2.3 用語定義
- **workflow**: ComfyUI の API 形式 JSON（UI 用 JSON ではなく、API 送出用のノード辞書）。
- **書き換え場所指定 text**: workflow 内に置かれた、meta 名 `fm_comfy_request` の multiline text ノード。内部は YAML 形式。
- **SdLoraYaml**: LoRA・サンプリング等の設定を保持する YAML 入出力クラス（旧モジュールで提供）。

## 3. パッケージ構成要求

### 3.1 パッケージ配置
- 配布パッケージ名は現行どおり `fm_comfyui_bridge`（`pyproject.toml` の `name` は変更しない）を維持する。
- パッケージ内に旧 API（`fm_comfyui_bridge.bridge` 等）と、新 API（`fm_comfyui_bridge.fm_comfy_request` 相当）の両方を提供する。
- 利用者は用途に応じて旧／新を選択的に `import` できること。

### 3.2 新モジュールの公開 API
- トップレベルで以下のカテゴリのエントリポイントを提供すること。
  - リクエスト実行（通常 / I2I）
  - ユーティリティ（メモリ解放、モデルリスト取得、PIL 変換、workflow 読み込み補助）
  - SdLoraYaml 拡張クラス
  - 例外クラス群
- 内部モジュールは論理的に分割する（例：workflow 操作、API 通信、LoRA 挿入、CLI）。具体的な分割は設計書で詳細化する。

## 4. Workflow 管理要求

### 4.1 Workflow の配置場所
- 旧モジュールのようにパッケージ内部に workflow を同梱しない。
- ユーザー配置ディレクトリ `~/.config/fm_comfy_request/workflow/` を基本配置先とする。
  - Windows 環境でもパス展開ルール上この配置で動作することを要求する（`pathlib.Path.home() / ".config" / ...` 相当の解決）。
- 配置ディレクトリは環境変数または関数引数で上書きできること（例：`FM_COMFY_REQUEST_WORKFLOW_DIR`）。
- workflow はファイル名（またはパス）で指定できる。絶対パス指定時はそのまま使用する。

### 4.2 Workflow の読み込み
- `.json` 形式の workflow ファイルを読み込めること。
- workflow の node ID は数値のみに限らず、`35:8` のような文字列形式も許容するものとして扱う。
- 読み込み時に、workflow 内に `fm_comfy_request` meta の multiline text ノードが存在することを確認する。
- 存在しない／記述不備の場合は専用例外を送出する。

### 4.3 Workflow の検証
- 以下について静的に検証し、不整合があれば例外で通知する。
  - 書き換え場所指定で指定されたノード名または node ID が workflow 内に存在すること。
  - I2I 要求時は `LoadImage` ノードの存在、および `input` キーでそのノードが指定されていること。

## 5. 書き換え場所指定 text（YAML）要求

### 5.1 形式
- workflow 内の multiline text ノードで、`_meta.title`（または `title`）が `fm_comfy_request` のものを 1 つ検出し、そのテキスト本体を YAML としてパースする。
- 複数存在した場合はエラーとする。

### 5.2 指定可能キー
以下のキーで workflow のノード名または node ID を指し示せること。全て省略可能だが、指定したキーは workflow 内に対応ノードが存在しなければならない。
- `model`: LoRA 挿入起点となる model 出力ソースノード名（checkpoint / diffusion model / 既存 LoRA ノード等）
- `clip`: clip 付き LoRA に使用する clip 出力ソースノード名（CLIP loader / checkpoint / 既存 LoRA ノード等）
- `prompt`: プロンプトテキストノード名
- `negative-prompt`: ネガティブプロンプトテキストノード名
- `seed`: シード値を持つノード名
- `seed-name`: `seed` ノード内でシード値を保持する入力キー名（省略時は `noise_seed`）
- `output`: SaveImage ノード名
- `input`: LoadImage ノード名（I2I 用）
- `size`: 画像サイズ指定ノード名（width/height を 1 ノードで持つ場合）
- `size-width`: width のみを持つノード名（size と分離型の場合）
- `size-height`: height のみを持つノード名（size と分離型の場合）
- `sampling-mode`: eps/v_prediction 切替ノード名
- `steps`: サンプリングステップ数を指定するノード名
- `cfg`: CFG スケールを指定するノード名

### 5.3 LoRA 挿入指定
- LoRA を挿入する workflow 側の接続点を YAML 上で明示できること。
- `model` は必須とし、LoRA 挿入の起点になる model 出力ソースを表す。
- `clip` は workflow により省略可能とする。checkpoint のように model ノード自身が clip 出力を持つ場合は省略できるが、`UNETLoader` + `CLIPLoader` のように model と clip が分離される workflow では、clip 付き LoRA を使う際に `clip` の指定を必須とする。
- workflow 内に固定 LoRA ノードが既に含まれている場合でも、そのノードを `model` / `clip` の起点として指定できること。

### 5.4 デフォルト値の扱い
- 書き換え場所指定で示されたノードの既存値を、リクエスト未指定時のデフォルト値として使用する。
- SdLoraYaml（後述）の値が存在する場合は、SdLoraYaml > workflow 既存値 の優先順位で適用する。
- リクエスト関数の引数で明示指定された値は最優先とする。

## 6. リクエスト API 要求

### 6.1 リクエスト種別
- 通常リクエスト（T2I 相当）と I2I リクエストの 2 種類を提供する。
- 旧モジュールの HighReso 相当 API は新モジュールでは提供しない（workflow 側で表現する）。
- I2I は workflow に `LoadImage` ノードが存在し、書き換え場所指定の `input` が有効な場合のみ呼び出し可能とする。条件未達時は呼び出し時点で例外とする。

### 6.2 必須／任意パラメータ
- **必須**: workflow 指定（ファイル名またはパス）
- **任意**:
  - `prompt`（省略時は workflow の既存値）
  - `negative`（省略時は workflow の既存値）
  - `SdLoraYaml` インスタンス（省略時は LoRA 挿入・サンプリング上書き等を行わない）
  - 接続先 URL（省略時は `http://127.0.0.1:8188/`、または環境変数の値）
  - 画像サイズ、seed、steps、cfg 等の個別パラメータ（省略時は SdLoraYaml → workflow の順に解決）
  - I2I 用入力画像（パスまたはバイナリ、I2I 時のみ）
- workflow のみを指定して呼び出した場合でも何らかの画像生成が成功することを保証する。

### 6.3 戻り値
- 画像はデフォルトでバイナリ（bytes 相当）として返す。これは ComfyUI 出力 PNG 内の meta 情報を損失なく保持するためである。
- PIL Image への変換はユーティリティ関数として別に提供する（利用者が明示的に変換する）。
- 生成結果には少なくとも以下の情報を含めて返すこと。
  - 画像バイナリ
  - 生成に使用された workflow（最終形）
  - prompt_id 等のトレーサビリティ情報
  - 出力ファイル名・サブフォルダ情報（ComfyUI からの応答由来）

### 6.4 接続先設定
- 接続先 URL は以下の優先順位で決定する。
  1. 関数引数
  2. 環境変数（例：`FM_COMFY_REQUEST_SERVER_URL`）
  3. デフォルト値 `http://127.0.0.1:8188/`

## 7. ユーティリティ要求

- **メモリ解放**: ComfyUI にモデルアンロードとメモリ解放を要求する機能（旧モジュールの `free` 相当）。
- **モデルリスト取得**: 指定フォルダ配下のモデル一覧を取得する機能（旧モジュールの `list_models` 相当）。
- **PIL 変換**: バイナリ画像を `PIL.Image` に変換する機能。
- **画像保存**: 旧モジュールの `save_image` 相当。バイナリ／PIL いずれからでも保存でき、ComfyUI 由来の PNG meta をバイナリから保存する場合は保持すること。
- **workflow 一覧**: 配置ディレクトリ内の workflow ファイルを列挙する機能。

## 8. LoRA 動的挿入要求

### 8.1 挿入仕様
- LoRA ノードの挿入位置は、書き換え場所指定で示された model ノードの直後で固定とする。
- 新規ノード ID は、既存 workflow の node ID が数値のみとは限らない前提で割り当てる。純数値の node ID が存在する場合はその最大値 + 1 以降を使用し、純数値 ID が存在しない場合は未使用の整数文字列を採用する。連続挿入時も重複しないこと。
- LoRA を複数指定した場合は、指定順にチェーン接続する。

### 8.2 LoRA 種別
- 以下 2 種類の LoRA ノードを使い分けられること。
  - **clip 付き LoRA（`LoraLoader` 等）**: model と clip の両方に影響。
  - **model LoRA（`LoraLoaderModelOnly` 等の model のみ挿入タイプ）**: model のみに影響。
- 切替は SdLoraYaml 側の `model_only` フラグに従う（後述）。
- clip 付き LoRA を挿入する場合、明示 `clip` 指定または `model` から導出できる CLIP 接続点のいずれかが必要であり、どちらも得られない場合は例外とする。

### 8.3 接続再配線
- 挿入時、元々 model/clip を参照していた下流ノードのリンクを、挿入された LoRA ノードの出力に差し替える。
- workflow 内に既存の固定 LoRA ノードが含まれる場合でも、`model` / `clip` で指定されたソースを起点に再配線できること。
- 旧モジュールの `replace_value_recursive` に相当するロジックを、新モジュール向けに汎用化した形で備えること（実装詳細は設計書）。

## 9. SdLoraYaml 拡張要求

### 9.1 拡張方針
- 旧 `SdLoraYaml` を継承、または互換スーパークラス化する形で新クラス（暫定名：`ConfigLoraYaml`）を提供する。
- 旧版 YAML ファイルがそのまま読み込めること。

### 9.2 追加項目
- `lora` リスト各要素に `model_only: [true|false]` を追加する。
  - `true`: model LoRA ノード（clip を繋がない）
  - `false` もしくは未指定: clip 付き LoRA ノード（従来どおり）

### 9.3 後方互換
- 旧 SdLoraYaml 利用時に新フィールドがあっても、旧コードの挙動に影響を与えないこと。
- 新モジュールで旧フォーマット YAML を読んだ場合、未記載パラメータは機能を無効にする側の値（例：`model_only` 未記載時は `false`）を返すこと。
- 旧クラスの既存 API（プロパティ名・シグネチャ）を破壊しないこと。

## 10. 通信・動作仕様要求

### 10.1 プロトコル
- ComfyUI のジョブ投入・結果取得には REST API を使用する（旧モジュール踏襲）。
- 実行状態の待機は WebSocket を使用する（旧モジュールのキューポーリングから刷新）。
  - WebSocket を通じて進捗（ステップ数、ノード実行状況等）のイベントを取り出せること。
  - 進捗を受け取るコールバック（またはイベントハンドラ）を呼び出し側が登録できること。

### 10.2 同期／非同期
- 同期 API と非同期 API の両方を提供する。
  - 同期 API：関数呼び出しで生成完了までブロックし、結果を返す。
  - 非同期 API：`asyncio` ベースで `await` 可能な形で結果を返す。
- 進捗コールバックは同期／非同期いずれの形態でも利用できること。

### 10.3 タイムアウト・リトライ
- 接続待ちのタイムアウト時間を設定可能とする（デフォルト値は本書では規定せず、設計書で定義）。
- 一過性の通信エラーについては、リトライ回数・間隔を設定可能とする。

## 11. 例外仕様要求

新モジュール専用の例外階層を設ける。少なくとも以下を区別できること。
- 基底例外（例：`FmComfyRequestError`）
- workflow 読み込み／解析失敗（ファイル無し、JSON 破損、meta ノード不在、YAML 解析失敗）
- workflow 内容不整合（指定ノード不在、I2I 不可 workflow への I2I 要求、LoRA 挿入に必要な接続点不在）
- ComfyUI への接続失敗
- ジョブ投入失敗（4xx/5xx 応答）
- WebSocket 通信エラー・切断
- タイムアウト
- 生成失敗（ComfyUI 側でエラー終了した場合）

例外メッセージには原因特定に十分な情報（対象 workflow ファイル、ノード名等）を含めること。

## 12. CLI 要求

### 12.1 目的
- `fm_comfy_request` の基本動作確認を容易にするため、CLI コマンドを提供する。
- pyproject.toml の `[project.scripts]` 等でエントリポイントを登録する。

### 12.2 最低限のサブコマンド／機能
- workflow 一覧表示（配置ディレクトリ内の workflow ファイル名）
- workflow の書き換え場所指定 YAML の表示・検証
- 画像生成（通常 / I2I）
  - workflow・prompt・negative・lora yaml・接続先 URL 等を引数で指定可能
  - 出力先ファイル名・ディレクトリを指定可能
  - 進捗を標準出力に表示できる
- モデル一覧取得（フォルダ指定）
- メモリ解放

### 12.3 非機能
- 終了コードで成功／失敗を区別する。
- 例外は人間可読なメッセージに整形して表示する（スタックトレースはデバッグオプション指定時のみ）。

## 13. 非機能要求

### 13.1 対応 Python バージョン
- 現行 `pyproject.toml` の `requires-python = ">=3.10"` を維持する。

### 13.2 依存関係
- 既存依存（`pillow`、`pyyaml`、`requests`）を維持する。
- 追加で以下の依存を許容する：
  - WebSocket クライアントライブラリ（`websocket-client` または `websockets` 等、設計書で選定）
  - 非同期 HTTP クライアント（非同期 API 実装に必要な場合、設計書で選定）
  - CLI フレームワーク（`argparse` で十分であれば不要、利便性が必要であれば `click` 等、設計書で選定）

### 13.3 テスト
- 既存 `tests/` と同一階層に新モジュール向けテストを追加する。
- 最低限以下の単体テストを備える。
  - 書き換え場所指定 YAML パース（正常系・異常系）
  - LoRA ノード挿入ロジック（clip 有／無、複数挿入、ID 割り当て）
  - I2I 可否判定
  - SdLoraYaml 拡張（新フィールドの有無に対する挙動）
- 可能な範囲で ComfyUI への通信はモック化し、ネットワーク不要で実行可能とする。

### 13.4 ドキュメント
- `README.md` に新モジュールの章を追加する、または別ファイルとして新モジュール向け README を用意する。
- 書き換え場所指定 YAML のサンプル、LoRA 挿入例、CLI 使用例を含めること。

### 13.5 ロギング
- 標準 `logging` モジュールでログを出力可能とする。CLI の詳細表示はログレベル切替で行う。

## 14. 後方互換性要求

- 旧モジュールの公開 API（`fm_comfyui_bridge.bridge` の関数群、`SdLoraYaml` クラス、既存 workflow 同梱）は、本件では変更しないか、変更する場合でも利用者コードの改修を必要としないこと。
- 既存利用者が現在のバージョン挙動のまま動作し続けられることを受け入れ条件とする。

## 15. 受け入れ条件（サマリ）

以下が全て満たされた時点で本要求を満たしたとみなす。
- 新モジュールが同一配布パッケージから `import` 可能で、旧モジュールと共存している。
- `~/.config/fm_comfy_request/workflow/` 配下の任意 workflow に対し、書き換え場所指定 YAML の記述のみで通常 / I2I 生成が実行できる。
- checkpoint 一体型 workflow と model / clip 分離型 workflow の双方で、LoRA の clip 有 / model only の切替および複数挿入が YAML 指定で動作する。
- 戻り値はバイナリで、meta 情報を保持した保存ができる。PIL 変換ユーティリティも利用できる。
- 同期 API で生成が可能で、非同期 API でも同等の生成が可能である。
- 進捗を受け取るコールバックが WebSocket 経由で機能する。
- CLI で最小限の生成・検証が完結する。
- 旧モジュール利用側のコードに改修が不要である。
