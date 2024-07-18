## Haipera: Convert Python scripts to reproducible production code

<img src="haipera_logo.jpg" alt="Haipera Logo" width="300"/>

[![License](https://img.shields.io/github/license/haipera/haipera)](https://github.com/haipera/haipera/blob/main/LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/haipera/haipera)](https://github.com/haipera/haipera/stargazers)

Find the right parameters and track experiments for your model without all the boilerplate.

[Join our Discord server!](https://discord.gg/UtHcwJzW)


## What is Haipera?

Haipera is an open-source framework to take scripts and make them 'production ready'.

- 🦥 **Config files without any code.** Automatically probes the source code to generate reproducible config files.
- 🐳 **Deploy on virtualenv for reproducible experiments.** Takes care of all the virtual environments of your code for maximum reproducibility of experiments.
- 🤖 **Setup grid search from CLI.** Use the command line to directly iterate through hyperparameters.
- 🪵 **Automatic experiment logging.** Automatically generates per-experiment output folders with reproducible configs.
- ☁️ **Hosted on the Cloud (coming soon!).** Run everything locally, or send your model to Haipera Cloud for parallel experimentation.

## Getting Started

Install haipera:

```
pip install haipera
```

Make sure you have a `requirements.txt` file where `script.py` or any Python script you want to run is (or alternatively, somewhere in the Git repo for the script).

Run scripts with:

```
haipera run script.py
```

See what options will be available with:

```
haipera run script.py --help
```

Running a script with `haipera` will generate a `script.toml` file where `script.py` is. 

You can directly 'edit' the config from CLI via:

```
haipera run script.py --options 123
```

You can also set up iterative experiments over parameters by:

```
haipera run script.py --option1 123 124 125 --option2 blue,red,green
```

Running `haipera` will also generate a `reports` folder where you run `haipera` from, with isolated experiment outputs in that folder.

You can also re-run existing configs reproducibly with:

```
haipera run reports/experiment/script.toml
```

## Have issues?

Haipera is still in its early stages, so it'll likely to have bugs. We're actively developing haipera, so if you file a GitHub issue or comment in the Discord server or drop us a line at support@haipera.com we will try to resolve them ASAP!
