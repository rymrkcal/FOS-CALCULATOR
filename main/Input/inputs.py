import json
import os
from datetime import datetime

DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def ask_text(prompt):
    while True:
        text = input(prompt).strip()
        if text != "":
            return text
        print("Enter text.")


def ask_float(prompt): 
    while True:
        text = input(prompt).strip()
        try:
            return float(text)
        except ValueError:
            print("Enter a number.")


def ask_float_not_zero(prompt):
    while True:
        number = ask_float(prompt)
        if number == 0:
            print("This value cannot be 0.")
        else:
            return number


def ask_int(prompt):
    while True:
        text = input(prompt).strip()
        try:
            count = int(text)
        except ValueError:
            print("Enter a whole number, at least 1.")
            continue
        if count < 1:
            print("Enter a whole number, at least 1.")
        else:
            return count


def ask_date(prompt):
    while True:
        text = input(prompt).strip()
        try:
            datetime.strptime(text, "%d-%m-%Y")
            return text
        except ValueError:
            print("Enter a date as DD-MM-YYYY.")


def ask_grade():
    while True:
        grade = input("Concrete grade (40, 50, or 60): ").strip()
        if grade == "40" or grade == "50" or grade == "60":
            return grade
        if grade == "C 40/50" or grade == "C 50/60" or grade == "C 60/75":
            return grade
        print("Enter 40, 50, or 60.")


def ask_humidity():
    while True:
        humidity = ask_float("RH (%): ")
        if humidity < 0 or humidity > 100:
            print("RH must be from 0 to 100.")
        else:
            return humidity


def ask_common_values():
    concrete_grade = ask_grade()
    sfc = ask_float_not_zero("SFC: ")
    pour_date = ask_date("Pour date (DD-MM-YYYY): ")
    rh = ask_humidity()

    ac = ask_float("Ac: ")
    ar = ask_float("Ar: ")
    while ac + ar == 0:
        print("Ac + Ar cannot be 0.")
        ac = ask_float("Ac: ")
        ar = ask_float("Ar: ")

    u = ask_float_not_zero("u: ")
    load = ask_float("Load: ")
    serial_no = ask_text("Serial number: ")
    return concrete_grade, sfc, pour_date, rh, ac, ar, u, load, serial_no


def ask_floor_counts():
    base_floor = ask_int("Base floor count: ")
    mid_floor = ask_int("Mid floor count: ")
    roof_floor = ask_int("Roof floor count: ")
    return base_floor, mid_floor, roof_floor

def ask_3l_values():
    print("3L input")
    concrete_grade, sfc, pour_date, rh, ac, ar, u, load, serial_no = ask_common_values()
    cs = ask_float("CS: ")
    ct = ask_float("CT: ")
    t_wavelength = ask_float("T wavelength: ")
    temperature = ask_float("Temperature: ")
    temp = ask_float("Temp: ")
    base_floor, mid_floor, roof_floor = ask_floor_counts()
    return {
        "concrete_grade": concrete_grade,
        "sfc": sfc,
        "t0": pour_date,
        "rh": rh,
        "ac": ac,
        "ar": ar,
        "u": u,
        "load": load,
        "serial_no": serial_no,
        "cs": cs,
        "ct": ct,
        "t_wavelength": t_wavelength,
        "temperature": temperature,
        "temp": temp,
        "base_floor": base_floor,
        "mid_floor": mid_floor,
        "roof_floor": roof_floor,
    }

def ask_atg_values():
    print("ATG input")
    concrete_grade, sfc, pour_date, rh, ac, ar, u, load, serial_no = ask_common_values()
    ks = ask_float_not_zero("Ks: ")
    ktt = ask_float_not_zero("Ktt: ")
    kts = ask_float("Kts: ")
    temp_fbg = ask_float("Temp-FBG: ")
    temp_fbg1 = ask_float_not_zero("Temp-FBG1: ")
    base_floor, mid_floor, roof_floor = ask_floor_counts()
    return {
        "concrete_grade": concrete_grade,
        "sfc": sfc,
        "t0": pour_date,
        "rh": rh,
        "ac": ac,
        "ar": ar,
        "u": u,
        "load": load,
        "serial_no": serial_no,
        "ks": ks,
        "ktt": ktt,
        "kts": kts,
        "Temp-FBG": temp_fbg,
        "Temp-FBG1": temp_fbg1,
        "base_floor": base_floor,
        "mid_floor": mid_floor,
        "roof_floor": roof_floor,
    }

def ask_readings():
    print("Measured strain")
    reading_count = ask_int("How many readings: ")
    readings = []
    reading_number = 1
    while reading_number <= reading_count:
        print("Reading", reading_number)
        sensor_measurement = ask_text("  Sensor measurement: ")
        reading_date = ask_date("  Reading date (DD-MM-YYYY): ")
        bot_strain = ask_float("  Bottom strain: ")
        bot_temp = ask_float("  Bottom temp: ")
        top_strain = ask_float("  Top strain: ")
        top_temp = ask_float("  Top temp: ")
        readings.append({
            "sensor_measurement": sensor_measurement,
            "date": reading_date,
            "bot_strain": bot_strain,
            "bot_temp": bot_temp,
            "top_strain": top_strain,
            "top_temp": top_temp,
        })
        reading_number = reading_number + 1
    return readings

def ask_stress_dates():
    print("Theoretical strain")
    date_count = ask_int("How many stress-history dates: ")
    stress_dates = []
    date_number = 1
    while date_number <= date_count:
        prompt = "  Stress-history date " + str(date_number) + " (DD-MM-YYYY): "
        stress_dates.append(ask_date(prompt))
        date_number = date_number + 1
    return stress_dates

def save_input(record):
    os.makedirs(DATA_FOLDER, exist_ok=True)
    file_path = os.path.join(DATA_FOLDER, record["calculation_id"] + ".json")
    if os.path.exists(file_path):
        print("File already exists:", file_path)
        return None
    with open(file_path, "x", encoding="utf-8") as file:
        json.dump(record, file, indent=2)
        file.write("\n")
    return file_path

def get_inputs():
    print("1) 3L")
    print("2) ATG")
    choice = input("Choice: ").strip()

    if choice == "1":
        sensor_type = "3L"
        parameters = ask_3l_values()
    elif choice == "2":
        sensor_type = "ATG"
        parameters = ask_atg_values()
    else:
        print("Enter 1 or 2.")
        return None

    readings = ask_readings()
    stress_dates = ask_stress_dates()
    calculation_id = sensor_type + "-" + datetime.now().strftime("%d%m%Y-%H%M%S")
    record = {
        "calculation_id": calculation_id,
        "sensor_type": sensor_type,
        "parameters": parameters,
        "readings": readings,
        "stress_dates": stress_dates,
    }

    saved_file = save_input(record)
    if saved_file is None:
        return None
    print("Input saved:", saved_file)
    return record

def collect():
    return get_inputs()
