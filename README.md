# Git PR data

## Table of content

[Introduction](#introduction)

[Installation](#installation)

[Usage](#usage)

[Pull Request Analysis](#)

[Change Classification](#)

[Change Rating](#)

[Contributing](#)

[License](#)

## Introduction

Git PR data is a python package to analyze a pull request from github using its [API](https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#get-a-pull-request)

## Installation

Clone project and find all necessary code under utils/pr_analyzer.py

## Usage

To analyze changes made in PR use function `get_data(git_pr_url: str)` under `utils/pr_analyzer.py`.
It returns all changes made through a tuple added_lines: list[str], removed_lines: list[str]

## Change classification

## Change rating

## Contributing

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).