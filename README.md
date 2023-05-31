# :sparkles: upset-alt-txt-gen ![Tests](https://github.com/visdesignlab/upset-alt-txt-gen/actions/workflows/tests.yml/badge.svg)
Design experiments for generating semantically meaningful alt-text. 
This work is adapted from:

```
Alan Lundgard AND Arvind Satyanarayan (2022). Accessible Visualization via 
Natural Language Descriptions: A Four-Level Model of Semantic Content. IEEE 
Transactions on Visualization & Computer Graphics (Proc. IEEE VIS).
```

## Local Deployment

1. Clone the repository using `git clone` or download and extract the zip file.
2. Ensure you have python version >= 3.10 installed.
3. Open a terminal in the repository directory and create and activate a python virtual environment running at least Python 3.10. For information on how to do this, navigate [here](https://docs.python.org/3/library/venv.html).
4. Install the required dependencies using `pip install -r requirements.txt`.
5. (Optional) Install the required development dependencies using `pip install -r requirements-dev.txt`. These are only required if you plan on running the tests or linting.
6. Install the alttxt module in development mode with `pip install -e .`

To run the alt-text-gen program, run `python3 [path/to/generator.py] --data [path/to/data] --grammar [path/to/grammar]`. See [Command Line Options](#command-line-options) for more information.

To run the program with the example data, run `python generator.py --data ../../data/simpson.json --grammar ../../data/grammar.json --level 2 --granularity medium` while in the `src/alttxt` directory.
Level and granularity can be changed to any of the options listed in [Command Line Options](#command-line-options).

## Local Testing

Local testing can be done using the `tox` command.

- Linting: To run the linting tests, run `tox -e lint`
- Type: To run the type tests, run `tox -e type`
- Tests: To run the python tests, run `tox -e test`
- Formatting: To automatically format the files to match the `flake8-black` standards, run `tox -e format`

To run the entire suite of tests at once, use `tox`.

## Command Line Options

| Command               | Description                                                                   |
|-----------------------|-------------------------------------------------------------------------------|
| `-h`, `--help`        | Show information on each command and exit.                                    |
| `-V`, `--version`     | Show the program version number and exit.                                     |
| `-D`, `--data`        | (Required) Relative path to data file.                                        |
| `-G`, `--grammar`     | (Required) Relative path to grammar file.                                     |
| `-l`, `--level`       | Semantic level. Defaults to `1`. Options are: `0`, `1`, `2`, and `3`.         |
| `-g`, `--granularity` | Alt-text granularity. Defaults to `medium`. Options: `low`, `medium`, `high`. |
