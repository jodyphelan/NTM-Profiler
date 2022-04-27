from pathogenprofiler import run_cmd
import pathogenprofiler as pp
import json
import os


if not os.path.isdir("scratch"):
    os.mkdir("scratch")
os.chdir("scratch")