import sys
import xml.etree.ElementTree as ET

MEMORY_SIZE = 1024

def load_binary(binary_file):
    """Загрузка бинарного файла."""
    with open(binary_file, "rb") as f:
        return list(f.read())

def execute_instruction(instr, memory):
    """Выполнение команды."""
    opcode = instr[0] & 0x7F
    if opcode == 94:  # LOAD_CONST
        b = (instr[1] | (instr[2] << 8) | (instr[3] << 16) | (instr[4] << 24))
        c = (instr[5] | (instr[6] << 8))
        memory[b] = c
        print(f"LOAD_CONST: memory[{b}] = {c}")
    elif opcode == 88:  # WRITE_MEM
        b = (instr[1] | (instr[2] << 8) | (instr[3] << 16) | (instr[4] << 24))
        c = (instr[5] | (instr[6] << 8) | (instr[7] << 16) | (instr[8] << 24))
        memory[b] = memory[c]
        print(f"WRITE_MEM: memory[{b}] = memory[{c}] = {memory[c]}")
    elif opcode == 9:  # READ_MEM
        b = (instr[1] | (instr[2] << 8) | (instr[3] << 16) | (instr[4] << 24))
        c = (instr[5] | (instr[6] << 8) | (instr[7] << 16) | (instr[8] << 24))
        d = (instr[9] | (instr[10] << 8))
        address = memory[c] + d
        memory[b] = memory[address]
        print(f"READ_MEM: memory[{b}] = memory[{address}] = {memory[address]}")
    elif opcode == 34:  # UNARY_SQRT
        if len(instr) < 11:
            raise ValueError(f"UNARY_SQRT: недостаточно данных в инструкции {instr}")

        b = (instr[1] | (instr[2] << 8) | (instr[3] << 16) | (instr[4] << 24))  # Адрес источника
        c = (instr[5] | (instr[6] << 8) | (instr[7] << 16) | (instr[8] << 24))  # Адрес назначения
        d = (instr[9] | (instr[10] << 8))  # Смещение

        if b >= len(memory):
            raise IndexError(f"UNARY_SQRT: адрес источника B={b} выходит за пределы памяти.")
        if c + d >= len(memory):
            raise IndexError(f"UNARY_SQRT: адрес назначения C+D={c + d} выходит за пределы памяти.")

        # Операция: sqrt
        value = memory[b]
        result = int(value ** 0.5)  # Квадратный корень, округленный до целого

        # Записываем результат в C + D
        memory[c + d] = result
        print(f"UNARY_SQRT: memory[{c + d}] = sqrt(memory[{b}]) = {result}")

    else:
        raise ValueError(f"Неизвестная команда с кодом {opcode}")

def interpret(binary_file, output_file, memory_range):
    memory = [0] * MEMORY_SIZE
    binary_data = load_binary(binary_file)
    i = 0
    while i < len(binary_data):
        opcode = binary_data[i]
        instr_size = 11 if opcode in (9, 34) else 7 if opcode == 94 else 9
        instr = binary_data[i:i + instr_size]
        i += instr_size
        execute_instruction(instr, memory)
    result = memory[memory_range[0]:memory_range[1]]
    save_result(output_file, result)

def save_result(output_file, result):
    root = ET.Element("result")
    for idx, value in enumerate(result):
        entry = ET.SubElement(root, "memory")
        entry.set("address", str(idx))
        entry.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(output_file)

if __name__ == "__main__":
    binary_file = sys.argv[1]
    output_file = sys.argv[2]
    memory_range = tuple(map(int, sys.argv[3:5]))
    interpret(binary_file, output_file, memory_range)
