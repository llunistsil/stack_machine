import pytest
import os
import tempfile
from src.compiler import compile
from src.machine import simulate

SOURCE = 'code.dr'
COMPILED = 'code.drc'
LOGFILE = 'log.log'
INPUT = 'input.txt'
OUTPUT = 'output.txt'


@pytest.mark.golden_test('golden/*.yaml')
def test_compiler_and_machine(golden):
    print('DEBUG golden type:', type(golden))
    print('DEBUG golden repr:', repr(golden))
    with tempfile.TemporaryDirectory() as tmpdir:
        source_code = os.path.join(tmpdir, SOURCE)
        input_data = os.path.join(tmpdir, INPUT)
        target = os.path.join(tmpdir, COMPILED)
        logfile = os.path.join(tmpdir, LOGFILE)

        with open(source_code, 'w', encoding='utf-8') as f:
            f.write(golden['in_source_code'])
        with open(input_data, 'w', encoding='utf-8') as f:
            f.write(golden['in_input_data'])

        error = compile.run(source_code, target)
        assert error is None

        # Читаем бинарник
        with open(target, 'rb') as f:
            binary = f.read()
        # Формируем расписание ввода (input_schedule)
        input_schedule = []
        if golden['in_input_data']:
            # Для простоты: каждый символ подаётся на такте i+1
            input_schedule = [(i+1, c) for i, c in enumerate(golden['in_input_data'])]
        # Запускаем симулятор
        output, _ = simulate(binary, input_schedule)
        # Читаем лог симуляции
        with open('simulation.log', 'r', encoding='utf-8') as f:
            sim_log = f.read()
        # Сравниваем с эталонами
        if 'out_output' in golden:
            assert output == golden['out_output'].strip()
        if 'out_log' in golden:
            # Сравниваем только значимые строки (без пустых)
            ref = [l.strip() for l in golden['out_log'].splitlines() if l.strip() and not l.strip().startswith('#')]
            got = [l.strip() for l in sim_log.splitlines() if l.strip()]
            assert got[:len(ref)] == ref