"""
    Agergador responsável pelos comandos reconhecidos.
"""

arguments = [
    {
        "name": ["--suite", "-s"],
        "kwargs": {
            "nargs": '+',
            "type": str,
            "help": 'Specify a suite name or a list of suites. Example: --suite suite1 suite2'
        }
    },
    {
        "name": ["--testcase", "-t"],
        "kwargs": {
            "nargs": '+',
            "type": str,
            "help": 'Specify a test id created in the suite file. Example: --testcase ACT_001 ACT_002'
        }
    },
    {
        "name": ["--datasetid", "-ds"],
        "kwargs": {
            "nargs": '?',
            "type": str,
            "const": '',
            "default": '',
            "help": 'Customize a BigQuery dataset name for run execution. Optional. Default is empty.'
        }
    },
    {
        "name": ["--run", "-r"],
        "kwargs": {
            "nargs": '?',
            "const": True,
            "default": True,
            "help": 'Generate a mock test without run results. Optional. Default is True.'
        }
    },
    {
        "name": ["--schema", "-sch"],
        "kwargs": {
            "action": 'store_true',
            "default": False,
            "help": 'Fetch the latest schema for mockup table ids from the BigQuery environment. Optional. Default is True.'
        }
    },
    {
        "name": ["--persist-dataset", "-p"],
        "kwargs": {
            "action": 'store_true',
            "help": 'Persist the dataset result after the test run in the BigQuery environment. Optional.'
        }
    }
]
