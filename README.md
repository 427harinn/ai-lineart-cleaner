# AI Lineart Cleaner

AI生成イラストを、白背景・指定色の線のPNG線画へ変換する小さなツールです。初期の線色は黒（`#000000`）です。CLIを維持しつつ、ブラウザからも試せます。ローカルPCへPythonやOpenCVを直接インストールする必要はなく、Dev ContainerまたはDockerで利用できます。

## 仕組みと制限

現在はグレースケール化した画像を固定しきい値で単純に二値化します。透明PNGの透明部分は白背景に合成し、しきい値以下を線、しきい値より明るい画素を白にします。デフォルトしきい値は **80** です。二値化後に黒い線画素だけを指定色へ置き換えるため、線画の抽出方法は変わりません。背景色は現在も白固定です。

- 低いしきい値: より暗い部分だけを黒にするため、薄い線・影を除外しやすくなります。
- 高いしきい値: 明るい部分まで黒になるため、薄い線を拾いやすい一方で影や塗りも残りやすくなります。

未対応: 線のかすれ補完、途切れた線の接続、線幅の均一化、髪や服などの選択領域を白くする処理、薄い線への高度な対応、色塗りのムラ補正。

## Dev Containerで開始する

Docker Desktop、VS Code、Dev Containers拡張機能を用意し、リポジトリを開いて **Dev Containers: Reopen in Container** を実行します。コンテナ内では依存関係が利用可能です。APIは自動起動しないため、必要に応じて次を実行します。

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

VS Codeから転送されたポート、または `http://localhost:8000` をブラウザで開きます。画像を選択すると元画像をプレビューできます。しきい値（0〜255、初期値80）はスライダーと数値入力で同期します。線色はカラーピッカーで選び、横に表示されるHEX値を確認できます。色の変更だけでは処理せず、**線画化** を押した時点のしきい値と線色が結果プレビュー・保存PNGへ反映されます。**PNGを保存** で直前の結果をダウンロードできます。

## CLI

PNGまたはJPEGを`input`に置き、次のように実行します。出力はPNGです。

```bash
python extract_lineart.py input/sample.png output/sample-lineart.png
python extract_lineart.py input/sample.png output/sample-60.png --threshold 60
python extract_lineart.py input/sample.png output/sample-brown.png --threshold 80 --line-color "#5A3A32"
```

`--line-color` は線色を `#RRGGBB` 形式（例: `#336699`）で指定します。省略時は黒（`#000000`）です。背景色は白固定です。

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
