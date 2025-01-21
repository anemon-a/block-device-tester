#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
import subprocess
import json
import logging

logging.basicConfig()
logger = logging.getLogger()
logger.level = logging.INFO


@dataclass
class Argument:
    name: str
    filename: str
    output: str


@dataclass
class FioTestResults:
    iodepths: list[int] = field(default_factory=lambda: [
                                1, 2, 4, 8, 16, 32, 64, 128, 256])
    latency: dict[list[float]] = field(default_factory=lambda: {
        "randread": [],
        "randwrite": []
    })

    def add_latency(self, operation: str, latency: float):
        self.latency[operation].append(latency)


def parse_arguments() -> Argument:
    parser = ArgumentParser(prog='blktest', description="")
    parser.add_argument("-name", required=True)
    parser.add_argument("-filename", required=True)
    parser.add_argument("-output", required=True)
    args = parser.parse_args()
    return Argument(args.name, args.filename, args.output)


def get_latency(data: str, rw: str) -> float:
    return float(json.loads(data)[
        'jobs'][0][rw[4:]]['lat_ns']['mean']) / 1e6


def run_fio(name: str, filename: str) -> FioTestResults:
    command = [
        'fio',
        f'--name={name}',
        f'--filename={filename}',
        '--ioengine=libaio',
        '--direct=1',
        '--bs=4k',
        '--numjobs=1',
        '--size=1G',
        '--runtime=15s',
        '--output-format=json',
        '--group_reporting'
    ]
    result = FioTestResults()
    logger.info('Выполняется тест fio %s:', name)
    for operation in ('randread', 'randwrite'):
        logger.info('Операция: %s', operation)
        for iodepth in result.iodepths:
            test_result = subprocess.run(command + [f'--rw={operation}',
                                                    f'--iodepth={iodepth}'], stdout=subprocess.PIPE, encoding="utf-8")
            latency = get_latency(test_result.stdout, operation)
            result.add_latency(operation, latency)
            logger.info('Iodepth: %s Avg. latency: %s', iodepth, latency)

    logger.info('Тест fio %s завершен.', name)
    return result


def write_data_in_file(result: FioTestResults) -> str:
    filename = 'data.txt'
    with open(filename, "w") as f:
        for x, y1, y2 in zip(result.iodepths, result.latency['randread'], result.latency['randwrite']):
            f.write(f"{x} {y1} {y2}\n")

    return filename


def create_plot(data_filename: str, image_name: str) -> None:
    gnuplot_script = f"""
set terminal pngcairo size 1000,600
set output '{image_name}'
set title 'График зависимости latency от iodepth для операций randread и randwrite'
set xlabel 'Iodepth'
set ylabel 'Latency'
set grid

set key inside bottom right

plot '{data_filename}' using 1:2 with linespoints lc rgb 'blue' title 'Randread', \
     '{data_filename}' using 1:3 with linespoints lc rgb 'red' title 'Randwrite'
"""

    process = subprocess.Popen(["gnuplot"], stdin=subprocess.PIPE, text=True)
    process.communicate(gnuplot_script)
    logger.info('График %s создан', image_name)


if __name__ == "__main__":
    args: Argument = parse_arguments()
    results: FioTestResults = run_fio(args.name, args.filename)
    filename = write_data_in_file(results)
    create_plot(filename, args.output)
