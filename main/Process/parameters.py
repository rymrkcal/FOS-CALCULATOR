F = 8
ES = 200
ECO = 21500
EC_FACTOR = 0.85
CTEA = 14.1
CTEB = 17.3
CTEC = 16.4
L1 = 0.006
L2 = 0.03
CC = 1000

def grade_values(concrete_grade):
    grade = str(concrete_grade).strip().upper()
    if grade == "40" or grade == "C 40/50":
        return 32, 28, "G40"
    if grade == "50" or grade == "C 50/60":
        return 40, 30, "G50"
    if grade == "60" or grade == "C 60/75":
        return 50, 32, "G60"
    raise ValueError("Concrete grade must be 40, 50, or 60.")

def fcm(fck):
    return fck + F

def eequ(fck, ac, sfc, ar):
    return (fck * ac / sfc + ES * ar) / (ac + ar)

def eci(fck):
    return ECO * (fck / F) ** (1 / 3)

def ec(eci_value):
    return EC_FACTOR * eci_value

def h(ac, u):
    return (2 * ac) / u

def strength(ec_grade, ac, ar):
    return ec_grade * ac + ES * ar

def eq_area(strength_value, ec_grade):
    return strength_value / ec_grade

def sigma(load, floors):
    return load * floors
