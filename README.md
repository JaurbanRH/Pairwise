# Pairwise
Pairwise is a tool for generating configurations using pairwise algorithm with weights.
## Installation
1. Clone this repo and change to cloned directory.
2. Install pipenv using pip: `pip install pipenv`
3. Install required packages: `pipenv install`

## Usage
Usage of this tool is very simple. 

First you need json file with parameters. e.g. `parameters.json`
```json
{
  "Parameters": {
    "P1": ["a", "b"],
    "P2": [1, 2],
    "P3": ["x", "y"]
  }
}
```
Then you can run it as `pipenv run pairwise parameters.json`

You must always run it from the root directory (/path/to/repository/Pairwise).

As output you get generated configurations:
```
 1: ['a', 2, 'y']
 2: ['a', 1, 'x']
 3: ['b', 1, 'y']
 4: ['b', 2, 'x']
```
You can also set weights for each parameter. e.g.
```json
{
  "Parameters": {
    "P1": ["a", "b"],
    "P2": [1, 2],
    "P3": ["x", "y"]
  },
  "Weights": {
    "a": 1,
    "x": 2
  }
}
```
Weight represents the ratio in which you want to parameters appear in generated configuratations.
Default weight for each parameter is 1.

Additionally, you can use some of the available options:
* `--output {file.csv}` creates csv file with generated configurations 
* `--margin {float}` margin of weights, some wiggle room for weight representation in generated configurations (default: 0.05)
* `--count` prints how many times was each parameter used during configuration generation

e.g. `pipenv run pairwise --output configurations.csv --margin 0.04 --count parameters.json` 