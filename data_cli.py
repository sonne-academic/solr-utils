#! /usr/bin/env python3
from data.commands import argument_parser
import logging

logging.basicConfig(level=logging.INFO)


def main():
    parser = argument_parser()
    args, unknown = parser.parse_known_args()
    kwargs = vars(args)
    func = kwargs.pop('func')
    func(**kwargs)
    pass


if __name__ == '__main__':
    main()
