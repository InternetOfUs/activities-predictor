"""main of the package"""

import argparse


def main(nbmax=None):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wenet activities predictor CLI")
    parser.add_argument("--nbmax", help="number max of users", type=int, default=None)
    args = parser.parse_args()
    main(nbmax=args.nbmax)
