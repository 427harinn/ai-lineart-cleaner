# AI Lineart Cleaner

AI生成イラストを、白背景・指定色の線のPNG線画へ変換する小さなツールです。初期の線色は黒（`#000000`）です。CLIを維持しつつ、ブラウザからも試せます。ローカルPCへPythonやOpenCVを直接インストールする必要はなく、Dev ContainerまたはDockerで利用できます。

## 仕組みと制限

現在はグレースケール化した画像を固定しきい値で単純に二値化します。透明PNGの透明部分は白背景に合成し、しきい値以下を線、しきい値より明るい画素を白にします。デフォルトしきい値は **80** です。二値化後に黒い線画素だけを指定色へ置き換えるため、線画の抽出方法は変わりません。背景色は現在も白固定です。

- 低いしきい値: より暗い部分だけを黒にするため、薄い線・影を除外しやすくなります。
- 高いしきい値: 明るい部分まで黒になるため、薄い線を拾いやすい一方で影や塗りも残りやすくなります。
- **薄い線補助**: OFFが初期値です。弱いCLAHE（局所コントラスト補正）と控えめな明度補正を二値化の前に適用し、背景に近い薄い線を拾いやすくします。ノイズや背景模様も増える可能性があります。
- **かすれ補完**: 初期値は「なし」（強度0）です。二値化後に小さな欠けをClosing処理で補います。強度1は3×3カーネルで1回、強度2は同じカーネルで2回処理します。強くすると近い線がつながる場合があります。

未対応: 髪や服などの黒い領域を白くする処理、完全に途切れた線の高度な接続、線幅の完全な均一化、AIによる領域認識。

## Dev Containerで開始する

Docker Desktop、VS Code、Dev Containers拡張機能を用意し、リポジトリを開いて **Dev Containers: Reopen in Container** を実行します。コンテナ内では依存関係が利用可能です。APIは自動起動しないため、必要に応じて次を実行します。

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

VS Codeから転送されたポート、または `http://localhost:8000` をブラウザで開きます。画像を選択すると元画像をプレビューできます。しきい値（0〜255、初期値80）はスライダーと数値入力で同期します。線色はカラーピッカーで選び、横に表示されるHEX値を確認できます。「薄い線を補助」はチェックボックスでONにでき、「かすれ補完」は「なし・弱い・やや強い」から選べます。設定変更だけでは処理せず、**線画化** を押した時点のすべての設定が結果プレビュー・保存PNGへ反映されます。**PNGを保存** で直前の結果をダウンロードできます。

## CLI

PNGまたはJPEGを`input`に置き、次のように実行します。出力はPNGです。

```bash
python extract_lineart.py input/sample.png output/sample-lineart.png
python extract_lineart.py input/sample.png output/sample-60.png --threshold 60
python extract_lineart.py input/sample.png output/sample-brown.png --threshold 80 --line-color "#5A3A32"
python extract_lineart.py \
  input/sample.png \
  output/sample-assisted.png \
  --threshold 80 \
  --line-color "#5A3A32" \
  --thin-line-assist \
  --repair-strength 1
```

`--line-color` は線色を `#RRGGBB` 形式（例: `#336699`）で指定します。省略時は黒（`#000000`）です。`--thin-line-assist` は薄い線補助を有効にします。`--repair-strength` は `0`（なし）、`1`（弱い）、`2`（やや強い）を指定でき、省略時は `0` です。補助を使うとノイズが増えたり、補完を強くすると近い線がつながったりする可能性があります。背景色は白固定です。

## Docker

ブラウザ版イメージをビルド・起動します。

```bash
docker build -t ai-lineart-cleaner .
docker run --rm -p 8000:8000 ai-lineart-cleaner
```

`http://localhost:8000` を開いてください。CLIもイメージ内で直接実行できます。

```bash
docker run --rm --entrypoint python \
  -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" \
  ai-lineart-cleaner extract_lineart.py input/sample.png output/sample-lineart.png
```

## テスト

Dev Container内で実行します。

```bash
python -m pytest
python -m py_compile extract_lineart.py app/*.py
python -m json.tool .devcontainer/devcontainer.json
git diff --check
```
