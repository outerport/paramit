## Haipera: Convert Python scripts and notebooks to reproducible production code

<img src="haipera_logo.jpg" alt="Haipera Logo" width="300"/>

[![License](https://img.shields.io/github/license/haipera/haipera)](https://github.com/haipera/haipera/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/haipera/haipera)](https://github.com/haipera/haipera/stargazers)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/12jY7Kr1Rupj-aJFjlIRgZf1x-nySQdoJ?usp=sharing)

Find the right parameters and track experiments for your model without all the boilerplate.

[Join our Discord server!](https://discord.gg/UtHcwJzW)

## What is Haipera?

Haipera is an open-source framework to take scripts and notebooks and make them 'production ready'.

- 🦥 **Config files without any code.** Automatically probes the source code to generate reproducible config files.
- 🐳 **Deploy on virtualenv for reproducible experiments.** Takes care of all the virtual environments (with auto-updates) of your code for maximum reproducibility of experiments.
- 🤖 **Setup grid search from CLI.** Use the command line to directly iterate through hyperparameters.
- 🪵 **Automatic experiment logging.** Automatically generates per-experiment output folders with reproducible configs.
- ☁️ **Hosted on the Cloud (coming soon!).** Run everything locally, or send your model to Haipera Cloud for parallel experimentation.

Other general features:

- supports `.ipynb` notebook files
- cached virtual environments
- debug as usual with `pdb`
- supports Windows, Linux, OSX
- saves console logs along with configs
- artifacts (images, models, etc) are also saved to separate experiment folders

#### What's next for haipera?

We want to support things like logging, experiment tracking, GPU profiling, along with a central web dashboard for everything all without having to write any custom code. Let us know at info@haipera.com if you have opinions- or if you have dying problems or needs that you want us to hear! We're all ears.

## Getting Started



Install haipera:

```
pip install haipera
```

If you want to use the notebook hosting, you can do

```
pip install "haipera[notebook]"
```

On Linux, you'll have to install a `venv` package, like:

```
apt install python3.10-venv
```

Make sure you have a `requirements.txt` file where `script.py` or any Python script you want to run is (or alternatively, somewhere in the Git repo for the script).

## Example of using haipera

In a typical project, you may set up a script like:

```python3
import numpy

num_apples = 100
apple_price = 3.0
print("# apples: ", num_apples)
print("price of an apple: ", apple_price)
price = num_apples * apple_price
print("total: ", price)
```

And in the same folder, you may have a `requirements.txt` that lists the dependencies:

```
numpy
```

This is a superficial example, but say you want to start experimenting with this code. You'll probably adjust `num_apples` and `apple_price` manually at first, but eventually you'll lose track of what changes caused the differences in the results, unless you diligently keep a lab notebook. 

To properly keep track of things, you need to often make it possible to edit these variables from command line interfaces, set up a notebook, set up a JSON or YAML file to keep track of this, log the outputs in a logging service, save the outputs / configs in a separate experiment folder, etc. There's a lot of work involved in making experimentation reproducible.

Haipera is designed to solve this. With haipera you can edit variables on the fly, which you can view with:

```
haipera run script.py --help
``` 

When you run haipera, you can pass in arguments without ever setting up `argparse`:
```
haipera run script.py --num-apples 30
```

This will also invoke a build of a virtual environment to run the code in, and generate a `script.toml` configuration file.

You can run these generated config files directly:

```
haipera run script.toml
```

You can also set up grid searches over parameters by:

```
haipera run script.py --num-apples 30,60 --apple-price 1.0,2.0
```

Running `haipera` will also generate a `reports` folder where you run `haipera` from, with isolated experiment outputs in that folder.

You can then re-run existing configs reproducibly with:

```
haipera run reports/experiment/script.toml
```

## Using haipera with Jupyter Notebooks

You can even run haipera with Jupyter notebooks! Using `haipera run` on a notebook file will run the notebook as a script. 

```
haipera run script.ipynb --num-apples 30
```

If you instead want to spin up a notebook with your chosen config, and have it run in an isolated environment (inside the generated `reports` folder), you can simply run the notebook with `haipera notebook`:

```
haipera notebook script.ipynb --num-apples 30
```

This will start a notebook server as usual with the provided configs, inside a dedicated folder inside `reports`.

This turns out to be a convenient way to do _versioning_ for notebooks- if you have a notebook that you want to use for different data or different examples, instead of cloning 8 versions of the same notebook, you can just have a single notebook and 8 different config files for those notebooks!

You can also run a Python script as a notebook, although usually there are probably not great reasons to do this.

## Demo on Google Colab
You can also try our Google Colab version which allows you to run Haipera in the cloud. Check out our Colab demo using the following notebook: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/12jY7Kr1Rupj-aJFjlIRgZf1x-nySQdoJ?usp=sharing)


## More examples

See https://github.com/haipera/haipera-samples for more complex examples that you can try running haipera on.


## Have issues?

Haipera is still in its early stages, so it'll likely to have bugs. We're actively developing haipera, so if you file a GitHub issue or comment in the Discord server or drop us a line at support@haipera.com we will try to resolve them ASAP!
