# AI Lineart Cleaner

AI生成の説明イラストを、資料やスライドで使いやすい白背景・黒線のPNG線画へ変換する小さなCLIツールです。画像をグレースケール化し、固定しきい値による二値化で暗い部分を黒線として抽出します。

Dockerを使って実行するため、ローカル環境にPython、OpenCV、NumPyを直接インストールする必要はありません。

## 必要なもの

- [Docker](https://www.docker.com/get-started/)

## Dockerイメージをビルドする

リポジトリのルートディレクトリで実行します。

```bash
docker build -t ai-lineart-cleaner .
```

## 実行方法（macOS / Linux）

変換したいPNGまたはJPEG画像を`input`ディレクトリに配置します。次のコマンドでは、`input/sample.png`を読み込み、変換結果を`output/sample-lineart.png`へ作成します。

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  ai-lineart-cleaner \
  input/sample.png output/sample-lineart.png
```

`output`ディレクトリが存在しない場合は、先に作成してください。

```bash
mkdir -p input output
```

しきい値を指定する場合は、末尾に`--threshold`を追加します。

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  ai-lineart-cleaner \
  input/sample.png output/sample-lineart.png \
  --threshold 160
```

## 実行方法（Windows PowerShell）

入力画像を`input`ディレクトリに配置してから、次のコマンドを実行します。出力画像は`output`ディレクトリに作成されます。

```powershell
docker run --rm `
  -v "${PWD}/input:/app/input" `
  -v "${PWD}/output:/app/output" `
  ai-lineart-cleaner `
  input/sample.png output/sample-lineart.png
```

しきい値の指定例:

```powershell
docker run --rm `
  -v "${PWD}/input:/app/input" `
  -v "${PWD}/output:/app/output" `
  ai-lineart-cleaner `
  input/sample.png output/sample-lineart.png `
  --threshold 160
```

PowerShellでディレクトリがまだない場合は、次のコマンドで作成できます。

```powershell
New-Item -ItemType Directory -Force input, output
```

## `--threshold` オプション

`--threshold`には`0`から`255`までの整数を指定できます。デフォルト値は`180`です。グレースケール化後、明るさがしきい値以下の画素を黒、それより明るい画素を白にします。濃い灰色や濃い茶色の輪郭線も、明るさがしきい値以下であれば抽出対象になります。透明なPNGは、透明部分を白背景として扱います。

- **しきい値を小さくする**: より暗い部分だけが黒線になります。薄い線や薄い影は除外されやすくなります。
- **しきい値を大きくする**: より明るい部分まで黒線になります。薄い線を拾いやすくなる一方、色塗りや影も線として抽出されやすくなります。

## 現在の制限

現段階では単純な二値化のみを行います。線のかすれ、途切れ、端点接続、線幅補正、色塗りのムラの補正には対応していません。実際のAI生成画像で結果を確認し、今後必要に応じて改善を検討してください。
