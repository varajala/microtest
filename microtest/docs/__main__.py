import sys
import os
from microtest.docs import generate_docs


def main(args):
    if len(args) != 2:
        print('\n == Python doc generator ==\n')
        print('Usage: [ package_root_folder ] [ docs_folder ]\n\n')
        print('package_root_folder:  A filepath to the packages "topmost" folder.')
        print('                      This contains the __init__.py - file.')
        print()
        print('docs_folder:          A filepath to the folder where the generated docs will be written.')
        print()
        return
    
    cwd = os.getcwd()
    pkg_path, docs_path = args[-2:]
    
    if not os.path.isabs(pkg_path):
        pkg_path = os.path.join(cwd, pkg_path)

    if not os.path.isabs(docs_path):
        docs_path = os.path.join(cwd, docs_path)

    generate_docs(pkg_path, docs_path)


if __name__ == '__main__':
    main(sys.argv[1:])
