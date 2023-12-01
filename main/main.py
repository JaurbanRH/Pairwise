"""Pairwise tool for generating configurations"""
import warnings

import click

from pairwise import Pairwise
from parameters_check import ParametersCheck


@click.command()
@click.argument("parameters", type=click.File("r"))
@click.option("-o", "--output", help="CSV output file", type=click.File("w"))
@click.option(
    "-m",
    "--margin",
    help="Margin of weights, default is 0.05",
    type=click.FLOAT,
)
@click.option("--count", help="Print how many times was each parameter used", is_flag=True)
def main(parameters, output, count, margin):
    """Main function for pairwise tool"""
    check = ParametersCheck(parameters)
    check.check_parameters()
    pairwise = Pairwise(check.file, margin)
    generated_all = pairwise.generate_configurations()
    pairwise.print_configurations()
    if not generated_all:
        warnings.warn("No more unique configuration meeting the requirements")
    if output:
        pairwise.to_csv(output)
    if count:
        pairwise.print_quantity()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
