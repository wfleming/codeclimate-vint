# Code Climate Engine to run Vint

[![Code Climate](https://codeclimate.com/github/wfleming/codeclimate-vint/badges/gpa.svg)](https://codeclimate.com/github/wfleming/codeclimate-vint)

A [Code Climate CLI][cli] [engine][spec] running the [Vint][vint] Vim Script linter.

[spec]: https://github.com/codeclimate/spec
[cli]: https://github.com/codeclimate/codeclimate
[vint]: https://github.com/Kuniwak/vint

## Installation

```
git clone https://github.com/wfleming/codeclimate-vint
cd codeclimate-vint
make
```

## Usage

**.codeclimate.yml**

```yml
engines:
  vint:
    enabled: true
```

```
codeclimate analyze --dev
```
