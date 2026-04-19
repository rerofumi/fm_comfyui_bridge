## 目的

- fm_comfyui_bridge の利用を拡大するために新しい ComfyUI アクセスモジュールを作成する
- 名前の候補は fm_comfy_request

## 作りたいもの

- ComfyUI workflow はモジュール内に抱え込まず ".config/fm_comfy_request/workflow/" に配置、参照する形にする
- ノード指定、書き換えはモジュール内で書き換え場所を指定せず、workflow 上に "fm_comfy_request" という meta名の multiline text ノード内に yaml 形式で記述、これを書き換え場所指定 text としモジュール側でその指定を読み取る
- ハイレゾリクエストは削除、通常リクエストと I2Iリクエストの 2種類
  - I2I が有効なのは workflow に LoadImage ノードがある場合のみ
- その他 Utility としてメモリ解放、モデルリスト取得
- 画像ダウンロードした後 PIL Image に変換せずバイナリとして扱う、ComfyUI 出力に含まれる meta を保持するため
  - PIL Image に変換する Util も用意する
- LoRA ノードは LoRA yaml 指定で workflow に差し込める
  - clip付き LoRA ノードと model LoRA ノードを区別して差し込める様にする
  - LoRA ノードは複数差し込める
- LoRA yaml のフォーマットは SdLoraYaml の旧版フォーマットとパラメータを引き継ぐ
  - clip付き/model LoRA ノードの区分を指定する "model_only: [true|false]" を lora 要素に追加する
- fm_comfy_request の簡易動作、確認を行うための CLI コマンドを作成する

## リクエストに必要な物

- workflow ファイル(必須)
- prompt(省略可), negative(省略可)
- workflow 設定を指定する SdLolaYaml インスタンス
- 接続先(省略可、省略時 http://127.0.0.1:8188/)
- パラメータ省略時は workflow 内の値をデフォルト値として使用
- workflow だけ指定すれば取りあえず何か生成される

## workflow 内の書き換え場所指定 text
workflow 内の以下のパラメータを書き換えられる等にノード名を記述する

```yaml
model: "load model ノード名"
prompt: "テキストプロンプトノード名"
negative-prompt: "テキストネガティブプロンプトノード名"
seed: "seed を持つノード名"
seed-name: "ノード内の実際のシード値を持つ要素名(デフォルトは noise_seed。実ノードに seed だけが存在する場合は seed にフォールバック)"
output: "SaveImage ノード名"
input: "LoadImage ノード名"
size: "出力画像サイズ設定ノード名"
size-width: "サイズが分かれているときの width 値設定ノード名"
size-height: "サイズが分かれているときの height 値設定ノード名"
sampling-mode: "eps/vpred を指定するノード名"
steps: "sampling steps を指定するノード名"
cfg: "sampling cfg を指定するノード名"
denoise: "I2I denoise 値を指定するノード名。値が小さいほど元画を保持する"
```

## 通信・動作仕様
- サーバーURLなどの接続設定は [環境変数 / 引数] から読み込む。
- 実行状態の待機には WebSocket を使用し、必要に応じて進捗(Progress)を取得できるコールバックを用意する。
- 処理モデルは [同期(Sync) / 非同期(Async)] ベースで実装する。
- 接続エラーや生成失敗時、タイムアウト時には適切なカスタム例外を送出する。

## LoRA 動的挿入の仕様
- LoRA ノードを差し込むノード位置は model ノードの直後で固定
- 新規追加する LoRA ノードの ID は、既存ワークフローの最大 ID + 1 以降を動的に割り当てる。
- 書き換え場所指定 text (YAML) には、LoRA を接続する対象となる Model ノードおよび CLIP ノードの識別子（または接続元/接続先の ID）を記述し、モジュール側でリンクの繋ぎ変えを行う。

## その他

- fm_comfy_request はこのプロジェクトの 1モジュールとして作成する
  - パッケージ名は fm_comfyui_bridge のままで、中に新旧 2つのパッケージがあり、利用者は好きな方を import して利用できる
- fm_comfy_request は既存の SdLoraYaml を利用し、追加要素は fm_comfyui_bridge.SdLoraYaml を拡張して良い
  - 旧版で新パラメータにアクセスすることはないが未記載のパラメータに関しては false 等の影響を与えない値を返す
