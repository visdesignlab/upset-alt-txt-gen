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
2. Open a terminal in the repository directory and create and activate a python virtual environment running at least Python 3.10. For information on how to do this, navigate [here](https://docs.python.org/3/library/venv.html).
3. Run `python3 setup.py install` while in the root path of the repository.

To run the alt-text-gen program, run `python3 [path/to/main.py] --data [path/to/data] --grammar [path/to/grammar]`. See [Command Line Options](#command-line-options) for more information.

## Local Testing

Local testing can be done using the `tox` command.

- Linting: To run the linting tests, run `tox -e lint`
- Type: To run the type tests, run `tox -e type`
- Tests: To run the python tests, run `tox -e test`
- Formatting: To automatically format the files to match the `flake8-black` standards, run `tox -e format`

To run the entire suite of tests at once, use `tox`.

## Command Line Options

| Command               | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `-h`, `--help`        | Show information on each command and exit.                                  |
| `-V`, `--version`     | Show the program version number and exit.                                   |
| `-D`, `--data`        | (Required) Relative path to data file.                                      |
| `-G`, `--grammar`     | (Required) Relative path to grammar file.                                   |
| `-l`, `--level`       | Semantic level. Defaults to 1. Options: `0`, `1`, `2`, `3`.                 |
| `-g`, `--granularity` | Alt-text granularity. Defaults to Medium. Options: `low`, `medium`, `high`. |
