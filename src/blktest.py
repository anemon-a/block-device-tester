from argparse import ArgumentParser, Namespace
import subprocess
import json


def parse_arguments() -> Namespace:
    parser = ArgumentParser(prog='blktest', description="")
    parser.add_argument("-name", required=True)
    parser.add_argument("-filename", required=True)
    parser.add_argument("-output", required=True)
    args = parser.parse_args()
    return args


def run_fio(name: str, filename: str) -> tuple[list[int], list[list[float]]]:
    command = [
        'fio',
        f'--name={name}',
        f'--filename={filename}',
        '--ioengine=libaio',
        '--direct=1',
        '--bs=4k',
        '--numjobs=1',
        '--size=1G',
        '--runtime=5s',
        '--output-format=json',
        '--group_reporting'
    ]

    operations = ('read', 'write')
    iodepths = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    latency = [[0] * len(iodepths) for _ in range(len(operations))]
    print(f'Выполняется тест fio {name}:')
    for i, rw in enumerate(operations):
        print(f'\tОперация: {rw}rand')
        for j, iodepth in enumerate(iodepths):
            data = subprocess.run(command + [f'--rw=rand{rw}',
                                             f'--iodepth={iodepth}'], stdout=subprocess.PIPE, encoding="utf-8")
            latency[i][j] = float(json.loads(data.stdout)[
                'jobs'][0][rw]['lat_ns']['mean']) / 1e6
            print(f'\t\tIodepth: {iodepth} Latency: {latency[i][j]}')

    print(f'Тест fio {name} завершен.')
    return iodepths, latency


def write_data_in_file(iodepths: list[int], latency: list[list[float]]) -> str:
    filename = 'data.dat'
    with open(filename, "w") as f:
        for x, y1, y2 in zip(iodepths, latency[0], latency[1]):
            f.write(f"{x} {y1} {y2}\n")

    return filename


def create_plot(data_filename: str, image_name: str) -> None:
    gnuplot_script = f"""
set terminal pngcairo size 1000,600
set output '{image_name}.png'
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
    print(f'График {image_name} создан')


if __name__ == "__main__":
    args = parse_arguments()
    iodepths, latency = run_fio(args.name, args.filename)
    filename = write_data_in_file(iodepths, latency)
    # filename = "data.dat"
    create_plot(filename, args.output)
