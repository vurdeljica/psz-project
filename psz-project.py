import argparse
import os, re, os.path

from argparse import RawTextHelpFormatter

usage_example = '''Usage example:

 python psz-project.py -p 1
 python psz-project.py -p 2 3 4
 python psz-project.py -c'''

absolute_path_to_script = os.path.abspath(os.path.dirname(__file__))

parser = argparse.ArgumentParser(description='PSZ project cli interface', formatter_class=RawTextHelpFormatter,
                                 epilog=usage_example, add_help=False)

optional_parameters = parser.add_argument_group('optional arguments')

optional_parameters.add_argument("-p", "--part", type=int, metavar='', required=False, nargs='+', choices=range(1, 7),
                                 help="choose which part do you want to run (can combine multiple parts): \n"
                                      "1 - Generate statistics \n"
                                      "2 - Data visualization \n"
                                      "3 - Run unsupervised clustering UI app \n"
                                      "4 - Run transcoding \n"
                                      "5 - Run resolving song ids synchronous (Sending 500 000 requests to server) \n"
                                      "6 - Run resolving song ids asynchronous (Sending 500 000 requests to server) \n")

optional_parameters.add_argument("-c", "--clean", required=False, action="store_true",
                                 help="clean all the generated results, except database")

optional_parameters.add_argument("-h", "--help", action="help", help="show this help message and exit")


args = parser.parse_args()


def clean_all():
    global absolute_path_to_script

    for directory_to_empty in ['statistics', 'visualization', 'unsupervised_learning-ui']:
        path_to_empty = absolute_path_to_script + "\\" + directory_to_empty + "\\results"
        for root, dirs, files in os.walk(path_to_empty):
            for file in files:
                os.remove(os.path.join(root, file))


def start_script(part):
    if part == 1:
        os.system('python ./statistics/statistics.py')
    elif part == 2:
        os.system('python ./visualization/visualization.py')
    elif part == 3:
        os.system('python ./unsupervised_learning-ui/unsupervised-learning.py')
    elif part == 4:
        os.system('python ./unsupervised_learning-ui/transcode.py')
    elif part == 5:
        os.system('python ./statistics/resolve_address.py')
    elif part == 6:
        os.system('python ./statistics/async_request.py')


if __name__ == '__main__':
    if args.clean:
        clean_all()
    else:
        if args.part is not None:
            for part in args.part:
                start_script(part)

