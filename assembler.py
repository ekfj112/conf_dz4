import sys
import xml.etree.ElementTree as ET

def parse_instructions(text):
    """Разбор инструкций из текстового файла."""
    instructions = []
    for line in text.strip().split("\n"):
        parts = line.split()
        opcode = parts[0]
        args = {k: int(v) for k, v in (arg.split("=") for arg in parts[1:])}
        instructions.append((opcode, args))
    return instructions

def encode_instruction(opcode, args):
    """Кодирование инструкции в байтовый формат."""
    if opcode == "LOAD_CONST":
        a = args['A']
        b = args['B']
        c = args['C']
        return [
            (a & 0x7F),  # Код операции (7 бит)
            (b & 0xFF), (b >> 8) & 0xFF, (b >> 16) & 0xFF, (b >> 24) & 0xFF,  # Поле B (32 бита)
            (c & 0xFF), (c >> 8) & 0xFF  # Поле C (12 бит, 2 байта)
        ]
    elif opcode == "WRITE_MEM":
        a = args['A']
        b = args['B']
        c = args['C']
        return [
            (a & 0x7F),
            (b & 0xFF), (b >> 8) & 0xFF, (b >> 16) & 0xFF, (b >> 24) & 0xFF,
            (c & 0xFF), (c >> 8) & 0xFF, (c >> 16) & 0xFF, (c >> 24) & 0xFF
        ]
    elif opcode == "READ_MEM" or opcode == "UNARY_SQRT":
        a = args['A']
        b = args['B']
        c = args['C']
        d = args['D']
        return [
            (a & 0x7F),
            (b & 0xFF), (b >> 8) & 0xFF, (b >> 16) & 0xFF, (b >> 24) & 0xFF,
            (c & 0xFF), (c >> 8) & 0xFF, (c >> 16) & 0xFF, (c >> 24) & 0xFF,
            (d & 0xFF), (d >> 8) & 0xFF
        ]
    else:
        raise ValueError(f"Неизвестная команда: {opcode}")

def save_binary(output_file, binary_data):
    """Сохранение бинарного файла и вывод его содержимого."""
    with open(output_file, "wb") as f:
        for instruction in binary_data:
            f.write(bytearray(instruction))
    print("Бинарные данные:")
    for instruction in binary_data:
        print(f"{list(instruction)}")

def save_log(log_file, instructions):
    """Сохранение XML-лога."""
    root = ET.Element("log")
    for idx, (opcode, args) in enumerate(instructions):
        entry = ET.SubElement(root, "instruction")
        entry.set("id", str(idx))
        for key, value in args.items():
            ET.SubElement(entry, key).text = str(value)
    tree = ET.ElementTree(root)
    tree.write(log_file)

def assemble(input_file, output_file, log_file):
    with open(input_file, 'r') as f:
        instructions = parse_instructions(f.read())
    binary_data = [encode_instruction(opcode, args) for opcode, args in instructions]
    save_binary(output_file, binary_data)
    save_log(log_file, instructions)

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    log_file = sys.argv[3]
    assemble(input_file, output_file, log_file)
