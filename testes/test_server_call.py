from subprocess import Popen
from subprocess import PIPE
import socket


def test_no_arguments():
    proc = Popen("python3 ../server.py", stdout=PIPE, shell=True)
    return_code = proc.wait()
    assert return_code == 1
    output = proc.stdout.read().decode('utf-8')
    assert output == "insuficiencia ou excesso de argumentos passados\n"


def test_too_many_arguments():
    proc = Popen("python3 ../server.py 1 2", stdout=PIPE, shell=True)
    return_code = proc.wait()
    assert return_code == 1
    output = proc.stdout.read().decode('utf-8')
    assert output == "insuficiencia ou excesso de argumentos passados\n"


def test_string_argument():
    proc = Popen("python3 ../server.py Im_a_string", stdout=PIPE, shell=True)
    return_code = proc.wait()
    assert return_code == 2
    output = proc.stdout.read().decode('utf-8')
    assert output == "tipo errado\n"


def test_negative_port():
    proc = Popen("python3 ../server.py -1", stdout=PIPE, shell=True)
    return_code = proc.wait()
    assert return_code == 2
    output = proc.stdout.read().decode('utf-8')
    assert output == "tipo errado\n"


def test_not_integer_port():
    proc = Popen("python3 ../server.py 123.4", stdout=PIPE, shell=True)
    return_code = proc.wait()
    assert return_code == 2
    output = proc.stdout.read().decode('utf-8')
    assert output == "tipo errado\n"


def test_out_of_range_port():
    proc = Popen("python3 ../server.py 100000", stdout=PIPE, shell=True)
    return_code = proc.wait()
    assert return_code == 2
    output = proc.stdout.read().decode('utf-8')
    assert output == "porto invalido\n"
