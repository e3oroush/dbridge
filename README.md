# dbridge

[![actions status](https://img.shields.io/github/actions/workflow/status/e3oroush/dbridge/publish-pypi.yml?branch=main&logo=github&style=)](https://github.com/e3oroush/dbridge/actions)
[![PyPI - Version](https://img.shields.io/pypi/v/dbridge.svg)](https://pypi.org/project/dbridge)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dbridge.svg)](https://pypi.org/project/dbridge)

---

A unified database management server that acts as a bridge between client applications and various database engines, providing a consistent interface for database operations and schema exploration.

This project is a server application that is intended to be used joined with a UI client that can seemlessly create different database connections to play around with.

## Table of Contents

- [Installation](#installation)
- [Run the Server](#run-the-server)
- [License](#license)

## Installation

```console
pip install dbridge
```

## Run the server

```console
pythom -m dbridge.server.app
```

## Features

- Supported DBs:
  - sqlite
  - duckdb
  - mysql
  - postgres
  - snowflake
- Get databases
- Get Schemas
- Get tables
- Get columns
- Run a sql file with multiple statements

## TODOs

- [ ] Autocomplete and suggestion
- [ ] Edit tables and schemas

## UIs

Here is a list of UI clients that are using this server to provide a dbridge user interface.

- [dbridge.nvim]() a neovim plugin

## License

`dbridge` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
