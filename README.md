# :sparkles: upset-alt-txt-gen ![Tests](https://github.com/visdesignlab/upset-alt-txt-gen/actions/workflows/tests.yml/badge.svg)
Design experiments for generating semantically meaningful alt-text for UpSet Plots.

## Local Deployment

1. Clone the repository using `git clone` or download and extract the zip file.
2. Ensure you have python version >= 3.8.10 installed.
3. Open a terminal in the repository directory and create and activate a python virtual environment running at least Python 3.8.10. For information on how to do this, navigate [here](https://docs.python.org/3/library/venv.html).
4. Install the required dependencies using `pip install -r requirements.txt`.
5. (Optional) Install the required development dependencies using `pip install -r requirements_dev.txt`. These are only required if you plan on running the tests or linting.
6. Install the alttxt module in development mode with `pip install -e .`


To run the program with the example data, run `python [path/to/alttxt directory] --data ../../data/movie_data_card_sort.json`
Level and granularity can be changed to any of the options listed in [Command Line Options](#command-line-options).
Here is an example command:
    For unix/macOS: `python3 src/alttxt --data data/movie_data_dev_sort.json`
    For Windows: `python src/alttxt --data data/movie_data_dev_sort.json`

## Local Testing

Local testing can be done using the `tox` command. Tests have not been updated to match the latest updates to the repository, and updating them is currently on hold, as deployment is a priority over robustness.

- Linting: To run the linting tests, run `tox -e lint`
- Type: To run the type tests, run `tox -e type`
- Tests: To run the python tests, run `tox -e test`
- Formatting: To automatically format the files to match the `flake8-black` standards, run `tox -e format`

To run the entire suite of tests at once, use `tox`.

## Command Line Options

| Command                | Description                                                                                     |
|------------------------|-------------------------------------------------------------------------------------------------|
| `-h`, `--help`         | Show information on each command and exit.                                                      |
| `-V`, `--version`      | Show the program version number and exit.                                                       |
| `-D`, `--data`         | (Required) Relative path to data file.                                                          |
| `-l`, `--level`        | Semantic level. Defaults to a combination of all levels. Options are: `1`, `2`.                 |
| `-st`, `--structured`  | Returns information in JSON format that contains structured text (long description), alt-txt (short description), and technical description of the plot making strategy                                                 |
| `-t`, `--title`        | A title for the plot; used in some generations. Defaults to `has no title`.                     |
|------------------------|     -------------------------------------------------------------------------------------------------|                   
