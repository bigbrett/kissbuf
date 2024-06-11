#!/usr/bin/python3

import re
from collections import defaultdict, deque

HEADER_FILE = 'example.h'
OUTPUT_FILE = 'generated_serde.c'
HEADER_OUTPUT_FILE = 'generated_serde.h'

primitive_types = {
    'int32_t': 4,
    'uint32_t': 4,
    'int16_t': 2,
    'uint16_t': 2,
    'float': 4,
    'double': 8,
    'uint8_t': 1
}

type_serializers = {
    'int32_t': 'serializeInt32LE',
    'uint32_t': 'serializeUint32LE',
    'int16_t': 'serializeInt16LE',
    'uint16_t': 'serializeUint16LE',
    'float': 'serializeFloatLE',
    'double': 'serializeDoubleLE',
    'uint8_t': 'serializeUint8'
}

type_deserializers = {
    'int32_t': 'deserializeInt32LE',
    'uint32_t': 'deserializeUint32LE',
    'int16_t': 'deserializeInt16LE',
    'uint16_t': 'deserializeUint16LE',
    'float': 'deserializeFloatLE',
    'double': 'deserializeDoubleLE',
    'uint8_t': 'deserializeUint8'
}

def parse_header(header_file):
    with open(header_file, 'r') as file:
        content = file.read()

    structs = re.findall(r'typedef\s+struct\s*\{([^}]*)\}\s*(\w+);', content)
    struct_dict = {}
    for struct in structs:
        struct_name = struct[1].strip()
        fields = struct[0].strip().split(';')
        field_list = []
        for field in fields:
            if field.strip():
                parts = field.strip().rsplit(' ', 1)
                type_name = parts[0].strip()
                var_name = parts[1].strip()
                field_list.append((type_name, var_name))
        struct_dict[struct_name] = field_list

    print("Parsed structs:", struct_dict)  # Debug statement

    return struct_dict

def compute_struct_size(struct_name, structs, primitive_types):
    if struct_name not in structs:
        raise KeyError(f"Unknown struct: {struct_name}")
    
    size = 0
    fields = structs[struct_name]
    for field in fields:
        type_name, _ = field
        if type_name in primitive_types:
            size += primitive_types[type_name]
        elif type_name in structs:
            size += compute_struct_size(type_name, structs, primitive_types)
        else:
            raise KeyError(f"Unknown type: {type_name}")
    return size

def resolve_dependencies(structs):
    dependency_graph = defaultdict(set)
    all_types = set(structs.keys())

    for struct_name, fields in structs.items():
        for field in fields:
            type_name, _ = field
            if type_name in all_types and type_name != struct_name:
                dependency_graph[struct_name].add(type_name)

    return dependency_graph

def topological_sort(dependency_graph):
    indegree = {node: 0 for node in dependency_graph}
    for node in dependency_graph:
        for neighbor in dependency_graph[node]:
            if neighbor not in indegree:
                indegree[neighbor] = 0
            indegree[neighbor] += 1

    queue = deque([node for node in dependency_graph if indegree[node] == 0])
    sorted_list = []

    while queue:
        node = queue.popleft()
        sorted_list.append(node)
        for neighbor in dependency_graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_list) != len(dependency_graph):
        raise ValueError("Cyclic dependency detected!")

    return sorted_list

def generate_helpers():
    helpers = """
void serializeInt32LE(int32_t value, uint8_t *buffer) {
    buffer[0] = (uint8_t)(value & 0xFF);
    buffer[1] = (uint8_t)((value >> 8) & 0xFF);
    buffer[2] = (uint8_t)((value >> 16) & 0xFF);
    buffer[3] = (uint8_t)((value >> 24) & 0xFF);
}

int32_t deserializeInt32LE(const uint8_t *buffer) {
    return (int32_t)buffer[0] |
           ((int32_t)buffer[1] << 8) |
           ((int32_t)buffer[2] << 16) |
           ((int32_t)buffer[3] << 24);
}

void serializeUint32LE(uint32_t value, uint8_t *buffer) {
    buffer[0] = (uint8_t)(value & 0xFF);
    buffer[1] = (uint8_t)((value >> 8) & 0xFF);
    buffer[2] = (uint8_t)((value >> 16) & 0xFF);
    buffer[3] = (uint8_t)((value >> 24) & 0xFF);
}

uint32_t deserializeUint32LE(const uint8_t *buffer) {
    return (uint32_t)buffer[0] |
           ((uint32_t)buffer[1] << 8) |
           ((uint32_t)buffer[2] << 16) |
           ((uint32_t)buffer[3] << 24);
}

void serializeInt16LE(int16_t value, uint8_t *buffer) {
    buffer[0] = (uint8_t)(value & 0xFF);
    buffer[1] = (uint8_t)((value >> 8) & 0xFF);
}

int16_t deserializeInt16LE(const uint8_t *buffer) {
    return (int16_t)buffer[0] |
           ((int16_t)buffer[1] << 8);
}

void serializeUint16LE(uint16_t value, uint8_t *buffer) {
    buffer[0] = (uint8_t)(value & 0xFF);
    buffer[1] = (uint8_t)((value >> 8) & 0xFF);
}

uint16_t deserializeUint16LE(const uint8_t *buffer) {
    return (uint16_t)buffer[0] |
           ((uint16_t)buffer[1] << 8);
}

void serializeFloatLE(float value, uint8_t *buffer) {
    uint32_t asInt = *(uint32_t*)&value;
    serializeUint32LE(asInt, buffer);
}

float deserializeFloatLE(const uint8_t *buffer) {
    uint32_t asInt = deserializeUint32LE(buffer);
    return *(float*)&asInt;
}

void serializeDoubleLE(double value, uint8_t *buffer) {
    uint64_t asInt = *(uint64_t*)&value;
    for (int i = 0; i < 8; ++i) {
        buffer[i] = (uint8_t)(asInt >> (i * 8));
    }
}

double deserializeDoubleLE(const uint8_t *buffer) {
    uint64_t asInt = 0;
    for (int i = 0; i < 8; ++i) {
        asInt |= ((uint64_t)buffer[i] << (i * 8));
    }
    return *(double*)&asInt;
}

void serializeUint8(uint8_t value, uint8_t *buffer) {
    buffer[0] = value;
}

uint8_t deserializeUint8(const uint8_t *buffer) {
    return buffer[0];
}
"""
    return helpers

def generate_prototypes(struct_name):
    prototypes = f"""
int {struct_name}Serialize(const {struct_name} *input, uint8_t *buffer, size_t bufferLen);
int {struct_name}Deserialize(const uint8_t *buffer, size_t bufferLen, {struct_name} *output);
"""
    return prototypes

def generate_serialize_function(struct_name, fields, structs):
    serialize_function = f"int {struct_name}Serialize(const {struct_name} *input, uint8_t *buffer, size_t bufferLen) {{\n"
    struct_size = compute_struct_size(struct_name, structs, primitive_types)
    serialize_function += f"    if (bufferLen < {struct_size}) {{\n"
    serialize_function += "        return -1; /* Buffer too small */\n"
    serialize_function += "    }\n\n"
    
    offset = 0
    for field in fields:
        type_name, var_name = field
        if type_name in type_serializers:
            serialize_function += f"    {type_serializers[type_name]}(input->{var_name}, buffer + {offset});\n"
            offset += primitive_types[type_name]
        elif type_name in structs:
            serialize_function += f"    {type_name}Serialize(&input->{var_name}, buffer + {offset}, bufferLen - {offset});\n"
            offset += compute_struct_size(type_name, structs, primitive_types)
        else:
            serialize_function += f"    memcpy(buffer + {offset}, &input->{var_name}, sizeof({type_name}));\n"
            offset += f"sizeof({type_name})"

    serialize_function += "\n    return 0; /* Success */\n"
    serialize_function += "}\n"
    return serialize_function

def generate_deserialize_function(struct_name, fields, structs):
    deserialize_function = f"int {struct_name}Deserialize(const uint8_t *buffer, size_t bufferLen, {struct_name} *output) {{\n"
    struct_size = compute_struct_size(struct_name, structs, primitive_types)
    deserialize_function += f"    if (bufferLen < {struct_size}) {{\n"
    deserialize_function += "        return -1; /* Buffer too small */\n"
    deserialize_function += "    }\n\n"
    
    offset = 0
    for field in fields:
        type_name, var_name = field
        if type_name in type_deserializers:
            deserialize_function += f"    output->{var_name} = {type_deserializers[type_name]}(buffer + {offset});\n"
            offset += primitive_types[type_name]
        elif type_name in structs:
            deserialize_function += f"    {type_name}Deserialize(buffer + {offset}, bufferLen - {offset}, &output->{var_name});\n"
            offset += compute_struct_size(type_name, structs, primitive_types)
        else:
            deserialize_function += f"    memcpy(&output->{var_name}, buffer + {offset}, sizeof({type_name}));\n"
            offset += f"sizeof({type_name})"

    deserialize_function += "\n    return 0; /* Success */\n"
    deserialize_function += "}\n"
    return deserialize_function

def generate_code(header_file, output_file, header_output_file):
    structs = parse_header(header_file)
    dependency_graph = resolve_dependencies(structs)
    sorted_structs = topological_sort(dependency_graph)
    
    with open(output_file, 'w') as file:
        file.write("#include <stdint.h>\n")
        file.write("#include <stddef.h>\n")
        file.write("#include <string.h>\n")
        file.write(f'#include "{header_output_file}"\n')
        file.write(f'#include "{header_file}"\n\n')
        
        file.write(generate_helpers())
        
        for struct_name in sorted_structs:
            fields = structs[struct_name]
            file.write("\n")
            file.write(generate_serialize_function(struct_name, fields, structs))
            file.write("\n")
            file.write(generate_deserialize_function(struct_name, fields, structs))

    with open(header_output_file, 'w') as header_file:
        header_file.write("#ifndef GENERATED_SERDE_H\n")
        header_file.write("#define GENERATED_SERDE_H\n\n")
        header_file.write(f'#include "{HEADER_FILE}"\n')
        header_file.write("#include <stdint.h>\n")
        header_file.write("#include <stddef.h>\n")
        header_file.write("\n")
        for struct_name in sorted_structs:
            header_file.write(generate_prototypes(struct_name))
        header_file.write("#endif /* GENERATED_SERDE_H */\n")

if __name__ == "__main__":
    generate_code(HEADER_FILE, OUTPUT_FILE, HEADER_OUTPUT_FILE)

