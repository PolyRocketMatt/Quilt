import argparse

from quilt.main import run_quilt

def main():
    parser = argparse.ArgumentParser(description='Run Quilt CLI')
    parser.parse_args()
    
    # Run Quilt
    run_quilt()


if __name__ == '__main__':
    main()