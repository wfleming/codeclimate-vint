#!/usr/bin/env python3.5

import importlib
import json
import os.path
import pkgutil
import sys
import vint.linting.policy

from pathlib import Path
from vint.linting.config.config_cmdargs_source import ConfigCmdargsSource
from vint.linting.config.config_container import ConfigContainer
from vint.linting.config.config_default_source import ConfigDefaultSource
from vint.linting.config.config_global_source import ConfigGlobalSource
from vint.linting.config.config_project_source import ConfigProjectSource
from vint.linting.env import build_environment
from vint.linting.file_filter import *
from vint.linting.level import Level
from vint.linting.linter import Linter
from vint.linting.policy_set import PolicySet


def import_all_policies():
    """
    Adapted from vint's bootstrap, which depends on where it's run from.
    """
    pkg_root = Path(vint.linting.policy.__file__).parent
    mod_iter = pkgutil.iter_modules(
            [str(pkg_root.resolve())],
            "vint.linting.policy.")
    for _, module_name, is_pkg in mod_iter:
        if not is_pkg:
            importlib.import_module(module_name)


class EngineConfig:
    include_paths = ["./"]

    def __init__(self, path):
        if os.path.exists(path):
            contents = open(path).read()
            config = json.loads(contents)

            if config.get("include_paths"):
                self.include_paths = config.get("include_paths")


class Issue:
    BASE_POINTS = 50000
    CATEGORY_MAPPINGS = {
        "ProhibitAutocmdWithNoGroup": "Bug Risk",
        "ProhibitCommandRelyOnUser": "Bug Risk",
        "ProhibitCommandWithUnintendedSideEffect": "Bug Risk",
        "ProhibitEncodingOptionAfterScriptEncoding": "Bug Risk",
        "ProhibitEqualTildeOperator": "Bug Risk",
        "ProhibitImplicitScopeBuitlinVariable": "Bug Risk",
        "ProhibitImplicitScopeVariable": "Bug Risk",
        "ProhibitMissingScriptEncoding": "Bug Risk",
        "ProhibitNoAbortFunction": "Bug Risk",
        "ProhibitSetNoCompatible": "Bug Risk",
        "ProhibitUnusedVariable": "Bug Risk",
        "ProhibitUsingUndeclaredVariable": "Bug Risk"
    }

    def __init__(self, violation):
        self.violation = violation

    def to_s(self):
        return json.dumps({
            "type": "issue",
            "check_name": self.violation["name"],
            "description": self.violation["description"],
            "content": {"body": self.violation["reference"]},
            "categories": [self._category()],
            "location": self._location(),
            "remediation_points": self.BASE_POINTS,
            "severity": self._severity()
        })

    def _category(self):
        return self.CATEGORY_MAPPINGS.get(self.violation["name"], "Style")

    def _location(self):
        return {"path": str(self.violation["position"]["path"]),
                "lines": {"begin": self.violation["position"]["line"],
                          "end": self.violation["position"]["line"]}}

    def _severity(self):
        if self.violation["level"] == Level.STYLE_PROBLEM:
            return "info"
        else:
            return "normal"


class Engine:
    def __init__(self):
        self.linter = self._build_linter()

    def analyze(self, config):
        for include_path in config.include_paths:
            path = Path(include_path)
            if path.is_dir():
                self._lint_files(find_vim_script([path]))
            elif bool(re.match(VIM_SCRIPT_FILE_NAME_PATTERNS, path.name)):
                self._lint_file(path)

    def _lint_files(self, paths):
        for path in paths:
            self._lint_file(path)

    def _lint_file(self, path):
        violations = self.linter.lint_file(path)
        for violation in violations:
            sys.stdout.write("%s\0" % Issue(violation).to_s())

    def _build_linter(self):
        env = build_environment({})
        vint_config = self._build_config_dict(env)
        policies = PolicySet()
        return Linter(policies, vint_config)

    def _build_config_dict(self, env):
        config = ConfigContainer(
            ConfigDefaultSource(env),
            ConfigGlobalSource(env),
            ConfigProjectSource(env),
            ConfigCmdargsSource(env),
        )

        return config.get_config_dict()

import_all_policies()

config = EngineConfig("/config.json")

if len(config.include_paths) > 0:
    Engine().analyze(config)
else:
    print("Empty workspace; skipping...", file=sys.stderr)
