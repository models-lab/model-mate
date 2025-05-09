import os
import sys

from argparse import ArgumentParser, Namespace

def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Process files with a given extension in a directory and write output to a file."
    )
    parser.add_argument(
        "-e", "--extension",
        required=True,
        help="File extension to search for (e.g., .txt)"
    )
    parser.add_argument(
        "-d", "--directory",
        required=True,
        help="Directory containing files"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path"
    )
    return parser.parse_args()

def main() -> None:
    args: Namespace = parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    files: list[str] = [
        f for f in os.listdir(args.directory)
        if f.endswith(args.extension)
    ]

    if not files:
        print(f"No files with extension '{args.extension}' found in '{args.directory}'.", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w") as out_f:
        for filename in files:
            out_f.write(f"{filename}\n")

    print(f"Listed {len(files)} files with extension '{args.extension}' in '{args.directory}' to '{args.output}'.")

if __name__ == "__main__":
    main()
