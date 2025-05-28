import sys
from .compile import run

def cli():
    if len(sys.argv) != 3:
        print(f'usage: {sys.argv[0]} src_file[.dr] output_file[.drc]')
        return

    src_file = sys.argv[1].strip()
    output_file = sys.argv[2].strip()

    if src_file == output_file:
        print("src file and output file shouldn't be equal", file=sys.stderr)
        return

    error = run(src_file, output_file)
    if error is not None:
        print(error, file=sys.stderr)

if __name__ == '__main__':
    cli() 