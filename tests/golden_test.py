import pytest
import os
import tempfile
from src.compiler import compile
from src.machine import simulate

SOURCE = 'code.dr'
COMPILED = 'code.drc'
INPUT = 'input.txt'


@pytest.mark.golden_test("golden/hello.yaml")
def test_compiler_and_machine(golden):
    print("Golden type:", type(golden))
    print("Golden repr:", repr(golden))

    with tempfile.TemporaryDirectory() as tmpdir:
        source_code = os.path.join(tmpdir, SOURCE)
        input_data = os.path.join(tmpdir, INPUT)
        target = os.path.join(tmpdir, COMPILED)

        # Записываем исходный код
        with open(source_code, 'w', encoding='utf-8') as f:
            f.write(golden._inputs['in_source_code'])

        # Записываем входные данные
        with open(input_data, 'w', encoding='utf-8') as f:
            f.write(golden._inputs['in_input_data'])

        # Компилируем
        error = compile.run(source_code, target)
        assert error is None

        # Читаем бинарник
        with open(target, 'rb') as f:
            binary = f.read()

        # Формируем расписание ввода
        input_schedule = []
        if golden._inputs.get('in_input_data', ''):
            input_schedule = [(i+1, c) for i, c in enumerate(golden._inputs['in_input_data'])]

        # Запускаем симулятор
        output, _ = simulate(binary, input_schedule)

        # Читаем лог
        with open('simulation.log', 'r', encoding='utf-8') as f:
            sim_log = f.read()

        # Проверяем вывод
        if 'out_output' in golden._inputs:
            assert output.strip() == golden._inputs['out_output'].strip()

        # Проверяем лог
        if 'out_log' in golden._inputs:
            ref = [l.strip() for l in golden._inputs['out_log'].splitlines() if l.strip() and not l.strip().startswith('#')]
            got = [l.strip() for l in sim_log.splitlines() if l.strip()]
            assert got[:len(ref)] == ref