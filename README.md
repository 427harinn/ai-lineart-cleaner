# AI Lineart Cleaner

AI生成の説明イラストを、資料やスライドで使いやすい白背景・黒線のPNG線画へ変換するPython CLIツールです。開発にはVSCode Dev Containerを、完成したCLIの実行には通常のDockerイメージを使用できます。いずれの場合も、ローカル環境へPython、OpenCV、NumPyを直接インストールする必要はありません。

## 現在の機能と制限

画像をグレースケール化し、固定しきい値以下の画素を黒、それより明るい画素を白にする単純な二値化のみを行います。濃い灰色や濃い茶色の線も、明るさがしきい値以下であれば抽出します。透明なPNGの透明部分は白背景として扱います。

線のかすれ補修、途切れた線の接続、線幅の均一化、色塗りのムラ補正には対応していません。

## 1. VSCode Dev Containerで開発する

### 必要なもの

- Docker Desktop
- Visual Studio Code
- VSCodeの[Dev Containers拡張機能](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### 開発環境を開始する

1. このリポジトリをVSCodeで開きます。
2. コマンドパレットから **`Dev Containers: Reopen in Container`** を実行します。Dockerfileや依存関係を変更した場合は、**`Dev Containers: Rebuild and Reopen in Container`** を使います。
3. 初回はDev ContainerイメージとPythonパッケージをビルドするため、完了まで時間がかかります。
4. 変換したいPNGまたはJPEG画像をワークスペース内の`input`ディレクトリへ置きます。
5. Dev Container内のVSCodeターミナルからCLIを実行します。開発時に、さらに`docker run`を実行する必要はありません。

```bash
python --version
python -c "import cv2, numpy; print(cv2.__version__)"
python extract_lineart.py input/sample.png output/sample-lineart.png
python extract_lineart.py \
  input/sample.png \
  output/sample-160.png \
  --threshold 160
```

変換結果はワークスペース内の`output`ディレクトリに作成されます。

## 2. 通常のDocker CLIとして実行する

この方法は、開発環境を開かずに完成したCLIを実行するためのものです。

### イメージをビルドする

リポジトリのルートで実行します。

```bash
docker build -t ai-lineart-cleaner .
```

### macOS / Linux

変換したい画像を`input`ディレクトリに置きます。`input`と`output`はコンテナの`/app/input`、`/app/output`へそれぞれマウントされ、出力画像はローカルの`output`ディレクトリに作成されます。

```bash
mkdir -p input output
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  ai-lineart-cleaner \
  input/sample.png output/sample-lineart.png \
  --threshold 180
```

### Windows PowerShell

入力画像を`input`ディレクトリに置いてから、次を実行します。

```powershell
New-Item -ItemType Directory -Force input, output
docker run --rm `
  -v "${PWD}/input:/app/input" `
  -v "${PWD}/output:/app/output" `
  ai-lineart-cleaner `
  input/sample.png output/sample-lineart.png `
  --threshold 180
```

## `--threshold` オプション

`--threshold`には`0`から`255`までの整数を指定できます。デフォルト値は`180`です。

- **しきい値を小さくする**: より暗い部分だけが黒線になります。薄い線や薄い影は除外されやすくなります。
- **しきい値を大きくする**: より明るい部分まで黒線になります。薄い線を拾いやすくなる一方、色塗りや影も線として抽出されやすくなります。

Docker CLIで`160`を指定する例:

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input" \
  -v "$(pwd)/output:/app/output" \
  ai-lineart-cleaner \
  input/sample.png output/sample-160.png \
  --threshold 160
```
