"""Presco pretix attendant data converter.

Usage:
  presco.py helios <pretix_csv> [--out=<out_name>]
  presco.py pizza <pretix_csv> [--out=<out_name>]

Options:
  -h --help         Show this screen.
  --out=<out_name>  Output with specific file name.
"""
import csv
from docopt import docopt
import pandas as pd
from pathlib import Path
import sys


REQ_COLS = {"Order code", "Product", "E-mail", "Your name:", "I hereby authorize:", "This person can be reached via the following email address:"}


def read_csv(csv_path_in):
    with csv_path_in.open() as f:
        data = pd.read_csv(f, sep=',', encoding='utf8')

    if REQ_COLS - set(data.columns.values):
        raise(ValueError)

    return data


def convert_helios(data):
    new_data = pd.DataFrame(columns=["voter_id", "e-mail", "name"])

    for i, row in data.iterrows():
        if row["Product"] == "I'm attanding the General Assembly":
            new_data = new_data.append({"voter_id": row["Order code"], "e-mail": row["E-mail"], "name": row["Your name:"]}, ignore_index=True)
        else:
            new_data = new_data.append({"voter_id": row["Order code"], "e-mail": row["This person can be reached via the following email address:"], "name": f"{row['I hereby authorize:']} gemachtigd door {row['Your name:']}"}, ignore_index=True)

    return new_data


def convert_pizza(data):
    new_data = pd.DataFrame(columns=["e-mail"])

    for i, row in data.iterrows():
        if row["Product"] == "I'm attanding the General Assembly":
            new_data = new_data.append({"e-mail": row["E-mail"]}, ignore_index=True)

    return new_data


if __name__ == "__main__":
    args = docopt(__doc__)

    csv_path_in = Path(args["<pretix_csv>"])

    try:
        data = read_csv(csv_path_in)
    except(ValueError):
        print("File does not contain the required columns", file=sys.stderr)
        exit()
    except(FileNotFoundError):
        print("Please provide a valid csv file", file=sys.stderr)
        exit()

    if (args["helios"]):
        csv_path_out = Path(args["--out"] or f"{csv_path_in.stem}_helios.csv")
        new_data = convert_helios(data)
    elif (args["pizza"]):
        csv_path_out = Path(args["--out"] or f"{csv_path_in.stem}_pizza.csv")
        new_data = convert_pizza(data)
    else:
        print("No valid conversion mode provided", file=sys.stderr)
        exit()

    new_data.to_csv(csv_path_out, mode='w', index=False, header=False, encoding='utf8')
