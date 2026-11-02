import json
import os

from Process.process import build_result


def print_table(title, rows):
    names = list(rows[0])
    table = []
    for row in rows:
        values = []
        for name in names:
            value = row[name]
            if type(value) == float:
                value = round(value, 4)
            values.append(str(value))
        table.append(values)

    widths = []
    for column in range(len(names)):
        width = len(names[column])
        for values in table:
            if len(values[column]) > width:
                width = len(values[column])
        widths.append(width)

    print()
    print(title)
    line = ""
    for column in range(len(names)):
        line = line + names[column].ljust(widths[column]) + "  "
    print(line)
    for values in table:
        line = ""
        for column in range(len(names)):
            line = line + values[column].ljust(widths[column]) + "  "
        print(line)


def save_result(calculation_id, sensor_type, result):
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), sensor_type)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, calculation_id + ".json")
    if os.path.exists(file_path):
        print("File already exists:", file_path)
        return None

    data = {
        "calculation_id": calculation_id,
        "sensor_type": sensor_type,
        "parameters": result["parameters"],
        "functions": result["functions"],
        "variables": result["variables"],
        "measured_strain": result["measured_strain"],
        "modulus": result["modulus"],
        "shrinkage": result["shrinkage"],
        "creep": result["creep"],
        "output": result["output"],
    }
    with open(file_path, "x", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
        file.write("\n")
    return file_path


def save_and_show(record):
    result = build_result(record) #proceed to process.py
    saved_file = save_result(record["calculation_id"], record["sensor_type"], result)
    if saved_file is None:
        return
    print("Output JSON:", saved_file)

    parameters = result["parameters"]
    if record["sensor_type"] == "3L":
        sensor_names = ["cs", "ct", "ctea", "cteb", "ctec", "l1", "l2", "cc"]
    else:
        sensor_names = ["ks", "ktt", "kts", "kst", "temp_fbg", "temp_kt"]
    names = ["grade", "fck", "fcm", "ec", "eequ"] + sensor_names + ["h", "strength", "eq_area"]

    print()
    print("PARAMETERS")
    for name in names:
        value = parameters[name]
        if type(value) == float:
            value = round(value, 6)
        print(name, "=", value)

    print()
    print("STRESS HISTORY")
    print("BASE =", parameters["base_stress_date"], "", round(parameters["sigma_base"], 4))
    print("MID =", parameters["mid_stress_date"], "", round(parameters["sigma_mid"], 4))
    print("ROOF =", parameters["roof_stress_date"], "", round(parameters["sigma_roof"], 4))

    print()
    print("FLOOR LEVEL")
    print("BASE=" + str(parameters["base_floor"]))
    print("MID=" + str(parameters["mid_floor"]))
    print("ROOF=" + str(parameters["roof_floor"]))

    print_table("MEASURED STRAIN", result["measured_strain"])
    print_table("STRAIN OUTPUT", result["output"])

    print()
    print("THEORETICAL")
    print_table("MODULUS OF ELASTICITY", result["modulus"])
    print_table("NOTIONAL SHRINKAGE", result["shrinkage"])
    print_table("CREEP", result["creep"])
