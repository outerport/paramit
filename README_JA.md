## paramit:コードを書かなくても始められるPythonスクリプトやNotebookの設定管理！

[![License](https://img.shields.io/github/license/haipera/paramit)](https://github.com/haipera/paramit/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/haipera/paramit)](https://github.com/haipera/paramit/stargazers)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/12jY7Kr1Rupj-aJFjlIRgZf1x-nySQdoJ?usp=sharing)
[![Twitter](https://img.shields.io/twitter/follow/haipera_ai?style=social)](https://twitter.com/haipera_ai)

えっボイラープレートを書かなくても設定管理ができる？再現性のあるスクリプトが書ける？NotebookをベースにCLIでハイパラサーチできる？勝手にフォルダ分けしてくれる？スクリプトから自動でGPUぶんまわそう！

[ディスコード!](https://discord.gg/UtHcwJzW)

<p align="center">
    <img src="demo.jpg" alt="Demo image for paramit" width="700"/>
</p>

## paramitってなに？

paramitは、スクリプトとノートブックからカスタムなコードを書かなくても「実験管理」を可能にするオープンソースフレームワークです。

- 🦥 **コード不要のコンフィグファイル。** ソースコードを自動解析して再現可能な設定ファイルを生成。
- 🐳 **仮想環境でデプロイして実験の再現性を確保。** 実験の再現性を最大化するため、仮想環境をすべて管理。
- 🤖 **CLIからハイパラチューニング。** コマンドラインから直接ハイパーパラメータを調整したり、グリッドサーチすることが可能。
- 🪵 **自動実験ログ記録。** 再現可能な設定を含む実験ごとの出力フォルダを自動生成。
- ☁️ **クラウドホスティング（近日公開予定！）。** ローカルで全て実行するか、Haiperaクラウドやあなたのクラウドアカウントにモデルを送信して並列実験が可能。


その他機能：

- `pip install paramit` だけでインストール！
- .ipynbノートブックファイルをスクリプトとして実行可能
- ノートブックサーバーの実行をサポート（設定管理付き！）
- 仮想環境のキャッシュ機能
- 通常通りpdbでデバッグ可能
- Windows、Linux、OSXをサポート
- 設定と共にコンソールログを保存
- 成果物（画像、モデルなど）も別の実験フォルダに保存

#### 実装予定の機能

- Bring-you-ownクラウドでのGPUトレーニングインフラ
- 自動ログ設定（wandb的な何か）
- GPUプロファイリングの自動計測
- LLMを活用したGPUプロファイル分析ダッシュボード
- 実験管理用Webダッシュボード

ご意見などありましたら、info@haipera.comまでお知らせください。また、解決したい切実な問題やニーズがあれば、いつでもお聞かせください！Twitterなどでも大丈夫です[@yongyuanxi](https://x.com/yongyuanxi)。

## paramitのはじめかた

インストール：
```
pip install paramit
```

ノートブック機能を使うには：
```
pip install "paramit[notebook]"
```

Linux環境だとVenv用のパッケージをインストールする必要があります。
```
apt install python3.10-venv
```

`script.py`や実行したいPythonスクリプトがある場所（または代替として、スクリプトのGitリポジトリ内のどこか）に`requirements.txt`ファイルがあることを確認してください。

## paramitの使い方

Pythonで色々と実験してる時、以下のようなスクリプトを書くことがあります：

```python3
import numpy

num_apples = 100
apple_price = 3.0
print("# apples: ", num_apples)
print("price of an apple: ", apple_price)
price = num_apples * apple_price
print("total: ", price)
```

同じフォルダに、Dependenciesをリストアップしたrequirements.txtがあるかもしれません：

```
numpy
```

あまり現実的ではない例ですが、このコードで実験を始めるとします。

まず最初は`num_apples`と`apple_price`を手動で調整したりして、どう結果が変わるかをみたりします。ただ、スクリプトが複雑化して変数が増えてきたり、メトリックスなどが増えてくるとだんだんとどのパラメータがどの結果とCorrespondするのかがわけわからなくなってきます。

これらの変数を追跡するには、これらの変数をコマンドラインインターフェースから編集できるようにしたり、ノートブックをセットアップしたり、これを追跡するためのJSONやYAMLファイルを設定したり、ログサービスに出力をログしたり、別々の実験フォルダに出力や設定を保存するなどが必要です。

実験を再現可能にするには**多くの作業**が必要で複雑なプロジェクトになると大変な量のボイラープレートが発生したりします。

paramitはこれを解決するために設計されています。paramitを使用すると、変数を設定管理のフレームワークを使用しなくても編集できます。

```
paramit run script.py --help
``` 

paramitを実行すると、`argparse`を設定しなくても引数を渡すことができます：

```
paramit run script.py --num-apples 30
```

paramitを走らせると、コードを実行するための仮想環境のビルドが呼び出され、`script.toml`設定ファイルが生成されます。

生成された設定ファイルを直接実行することもできます：

```
paramit run script.toml
```

パラメータのグリッドサーチを設定することもできます（例えばこの例だと４つの実験がスケジュールされます）：

```
paramit run script.py --num-apples 30,60 --apple-price 1.0,2.0
```

paramitを実行すると、paramitを実行した場所にreportsフォルダが生成され、そのフォルダ内に独立した実験出力が保存されます。

既存の設定を再現可能に再実行するには：

```
paramit run reports/experiment/script.toml
```

## Using paramit with Jupyter Notebooks

Jupyterノートブックでもparamitを実行できます！

ノートブックファイルで`paramit run`を使用すると、ノートブックをスクリプトとして実行します。

これは、ノートブック環境でスクリプトを開発し、その後多くのパラメータにわたって実行をスケールアウトしたい場合に便利です。

```
paramit run script.ipynb --num-apples 30,40,50
```

CLIからの設定でノートブックを起動し、分離された環境（生成されたreportsフォルダ内）で実行したい場合は、`paramit notebook`を使うことでノートブックサーバーを実行できます：

```
paramit notebook script.ipynb --num-apples 30
```

これにより、提供された設定で通常通りノートブックサーバーが起動し、reports内の専用フォルダ内で実行されます。

Reports内で生成された設定（Config）ファイルはノートブックのバージョン管理としても使えたりします。異なるデータや異なる例に使用したいノートブックがある場合、同じノートブックの8つのクローンを作成する代わりに、単一のノートブックと8つの異なる設定ファイルを用意するだけで済みます！

## Demo on Google Colab

クラウドでparamitを実行できるGoogle Colabバージョンも試すことができます:  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/12jY7Kr1Rupj-aJFjlIRgZf1x-nySQdoJ?usp=sharing)

## More examples

paramitで実行できるより複雑な例については、https://github.com/haipera/haipera-samples をご覧ください。

## Have issues?

paramitはまだ初期段階にあるため、バグがある可能性が高いです。GitHubでイシューを立てるか、Discordサーバーでコメントするか、support@haipera.comまでメールを送っていただければ、できるだけ早く解決するよう努めます！
