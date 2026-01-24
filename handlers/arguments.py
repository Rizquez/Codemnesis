# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from __future__ import annotations

import os
from typing import TYPE_CHECKING
from argparse import ArgumentParser

if TYPE_CHECKING:
    from argparse import Namespace
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

class Arguments:
    """
    Class responsible for managing and validating arguments received by the console.

    **Purpose:**
        - Define the required and optional arguments for execution.
        - Parse the values entered by the user.
        - Apply basic validations on the arguments received.
        - Return the arguments as a `Namespace` object ready for use.
    """

    @classmethod
    def get(cls) -> Namespace:
        """
        Defines, processes, and validates console arguments for algorithm execution.

        Returns:
            Namespace: 
                Object with parsed and validated arguments.
        """
        parser = ArgumentParser(
            description="Required and optional arguments for executing the algorithm"
        )
        
        parser.add_argument(
            '--framework',
            required=True,
            choices=['csharp', 'python'],
            help="Programming languages and frameworks supported by the algorithm"
        )

        parser.add_argument(
            '--repository',
            required=True,
            help="Directory of the repository hosting the project"
        )

        parser.add_argument(
            '--output',
            help="Directory where the generated files will be stored"
        )

        parser.add_argument(
            '--excluded',
            help="Additional files/extensions to exclude from the scan, separated by commas if multiple are specified"
        )

        args = parser.parse_args()

        cls.__validate(args, parser)

        return args

    @staticmethod
    def __validate(args: Namespace, parser: ArgumentParser) -> None:
        """
        Performs validations on arguments received from the console.

        Args:
            args (Namespace): 
                Arguments parsed from the console.
            parser (ArgumentParser): 
                Parser used to throw error messages.

        Raises:
            SystemExit: 
                If any validation fails, `parser.error` is invoked, which stops execution 
                and displays the corresponding error message.
        """
        if not os.path.exists(args.repository):
            parser.error("The parameter sent in `--repository` must be a valid directory!")

        if args.output and not os.path.exists(args.output):
            parser.error("The parameter sent in `--output` must be a valid directory!")

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE