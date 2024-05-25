## Haipera: Run Python scripts reproducibly with no-code auto-config

<img src="haipera_logo.jpg" alt="Haipera Logo" width="300"/>

[![License](https://img.shields.io/github/license/username/repo)](https://github.com/haipera/haipera/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/username/repo)](https://github.com/haipera/haipera/stargazers)

Find the right parameters and track experiments for your model without all the boilerplate.

[Join our Discord server!](https://discord.gg/z8SZUBKt)


## What is Haipera?

Haipera is an open-source framework for auto-configurating and performing hyperparameter tuning on your models:

- 🦥 **Config files without any code.** Automatically probes the source code to generate reproducible config files.
- 🐳 **Deploy on virtualenv for reproducible experiments.** Takes care of all the virtual environments of your code for maximum reproducibility of experiments.
- 🤖 **Setup ablation studies from CLI.** Use the command line to directly iterate through hyperparameters.
- ☁️ **Hosted on the Cloud (coming soon!).** Run everything locally, or send your model to Haipera Cloud for parallel experimentation.

## Getting Started

Install haipera:

```
pip install haipera
```

Make sure you have a `requirements.txt` file where `script.py` or any Python script you want to run is (or alternatively, somewhere in the Git repo for the script).

Generate config files for your model with:

```
haipera run script.py
```

This will generate a `script.toml` file where `script.py` is. 

You can directly 'edit' the config from CLI via:

```
haipera run script.py --options 123
```

You can also set up iterative experiments over parameters by:

```
haipera run script.py --option1 123 124 125 --option2 blue,red,green
```
