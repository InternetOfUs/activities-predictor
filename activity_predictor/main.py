"""main of the package"""

import argparse


def main(nbmax=None, do_loop=False, delta_hours=12):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wenet activities predictor CLI")
    parser.add_argument("--nbmax", help="number max of users", type=int, default=None)
    parser.add_argument(
        "--do_loop", help="if enabled, this will loop forever", action="store_true"
    )
    parser.add_argument(
        "--delta_hours",
        help="set the number of hours before each loop (if loop is enabled)",
        type=int,
        default=12,
    )
    args = parser.parse_args()
    main(nbmax=args.nbmax, do_loop=args.do_loop, delta_hours=args.delta_hours)
