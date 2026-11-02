def avg_strain(bot_strain, top_strain):
    return (bot_strain + top_strain) / 2

def avg_temp(bot_temp, top_temp):
    return (bot_temp + top_temp) / 2

def change_strain(row_number, avg_strain, first_strain):
    if row_number == 1:
        return 0.0
    return avg_strain - first_strain

def change_temp(row_number, avg_temp, first_temp):
    if row_number == 1:
        return 0.0
    return avg_temp - first_temp

def ct_term(ct, cc, change_temp):
    return ct * cc * change_temp

def measured_3l(row_number, cs, cc, change_strain, ct_term, ctea, cteb, l1, ctec, l2):
    if row_number == 1:
        return 0.0
    return cs * cc * change_strain - ct_term * ctea + ct_term * cteb * l1 + ct_term * ctec * l2

def temp_c_3l(ct, avg_temp, t_wavelength, cc, temp, temperature):
    return ct * ((avg_temp - t_wavelength) * cc) + temp + temperature

def kst(kts, ktt):
    if ktt == 0:
        return None
    return kts / ktt

def base_reading(row_number, current, second):
    if row_number < 3:
        return current
    return second

def measured_atg(avg_strain, base_strain, avg_temp, base_temp, kst_value, ks):
    if ks is None or ks == 0 or kst_value is None:
        return None
    return ((avg_strain - base_strain) - (avg_temp - base_temp) * kst_value) / ks

def temp_c_atg(avg_temp, temp_fbg, temp_kt):
    if temp_kt == 0:
        return None
    return (avg_temp - temp_fbg) / temp_kt
