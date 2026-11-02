import math
from datetime import date, datetime

FCM0 = 10
BETA_SC = 5
S = 0.25
RH0 = 100
T0 = 28
TS = 0
T1 = 1
H0 = 100

def to_date(value):
    if type(value) == datetime:
        return value.date()
    if type(value) == date:
        return value
    return datetime.strptime(str(value).strip(), "%d-%m-%Y").date()

def pour_day(pour_date, stress_dates):
    if pour_date is not None and str(pour_date).strip() != "":
        return to_date(pour_date)
    return to_date(stress_dates[0])

def age_days(day, poured):
    return (to_date(day) - poured).days

def loading_age_for_creep(age):
    if age is None:
        return None
    if age <= 0:
        return 1
    return age

def floor_date(stress_dates, floor_number):
    place = int(floor_number)
    if place < 1 or place > len(stress_dates):
        raise ValueError("Floor level is outside the stress-history dates.")
    return to_date(stress_dates[place - 1])

def ME_cc(age):
    if age is None or age <= 0:
        return None
    denom = age / T1
    if denom <= 0:
        return None
    ratio = T0 / denom
    if ratio < 0:
        return None
    return math.exp(S * (1 - math.sqrt(ratio)))

def ME_E(me_cc, eci_value):
    if me_cc is None or eci_value is None:
        return None
    return math.sqrt(me_cc)

def eci_t(me_e, eci_value):
    if me_e is None or eci_value is None:
        return None
    return me_e * eci_value

def total_load(load, row_number):
    return load * row_number

def stress_inc(load):
    return load

def eps_s_fcm(fcm, h):
    if h is None or h <= 0 or fcm is None:
        return None
    return (160 + 10 * BETA_SC * (9 - fcm / FCM0)) * 10 ** -6

def NS_sRH(rh, h, fcm):
    if h is None or h <= 0 or fcm is None:
        return None
    return 1 - (rh / RH0) ** 3

def NS_RH(ns_srh):
    if ns_srh is None:
        return None
    return -1.55 * ns_srh

def eps_cs0(eps_s_fcm_value, ns_rh):
    if eps_s_fcm_value is None or ns_rh is None:
        return None
    return eps_s_fcm_value * ns_rh

def NS_s(age, h, fcm):
    if h is None or h <= 0 or fcm is None:
        return None
    shrink_time = (age - TS) / T1
    shrink_denom = 350 * (h / H0) ** 2 + shrink_time
    if shrink_denom == 0 or shrink_time / shrink_denom < 0:
        return None
    return math.sqrt(shrink_time / shrink_denom)

def eps_shrinkage(eps_cs0_value, ns_s):
    if eps_cs0_value is None or ns_s is None:
        return None
    return eps_cs0_value * ns_s * 10 ** 6

def C_RH(rh, h, fcm):
    if h is None or h <= 0 or fcm is None or fcm <= 0:
        return None
    return 1 + ((1 - rh / RH0) / (0.46 * (h / H0) ** (1 / 3)))

def C_fcm(fcm, h):
    if h is None or h <= 0 or fcm is None or fcm <= 0:
        return None
    return 5.3 / math.sqrt(fcm / FCM0)

def C_t0(loading_age):
    if loading_age is None or loading_age <= 0:
        return None
    return 1 / (0.1 + (loading_age / T1) ** 0.2)

def C_0(c_rh, c_fcm, c_t0):
    if c_rh is None or c_fcm is None or c_t0 is None:
        return None
    return c_rh * c_fcm * c_t0

def C_H(rh, h, fcm):
    if h is None or h <= 0 or fcm is None or fcm <= 0:
        return None
    return 150 * (1 + (1.2 * rh / RH0) ** 18) * (h / H0) + 250

def C_c(age, loading_age, c_h):
    if c_h is None or age is None or loading_age is None:
        return None
    creep_time = (age - loading_age) / T1
    creep_denom = c_h + creep_time
    if creep_denom == 0 or creep_time / creep_denom < 0:
        return None
    return (creep_time / creep_denom) ** 0.3

def C_t(c_0, c_c):
    if c_0 is None or c_c is None:
        return None
    return c_0 * c_c

def eps_creep(creep_load_value, eci_t_value, c_t):
    if c_t is None or eci_t_value is None or eci_t_value == 0 or creep_load_value is None:
        return None
    return (creep_load_value / eci_t_value) * c_t * 10 ** 6

def shrinkage(eps_shrinkage_value):
    return eps_shrinkage_value

def creep(eps_creep_value):
    return eps_creep_value

def elastic(stress, eequ_value):
    if eequ_value is None or eequ_value == 0 or stress is None:
        return None
    return (stress / eequ_value) * 1000

def total_ts(shrinkage_value, creep_value, elastic_value):
    if shrinkage_value is None or creep_value is None or elastic_value is None:
        return None
    return shrinkage_value + creep_value + elastic_value