from Process.measured_strain import (
    avg_strain,
    avg_temp,
    base_reading,
    change_strain,
    change_temp,
    ct_term,
    kst,
    measured_3l,
    measured_atg,
    temp_c_3l,
    temp_c_atg,
)
from Process.parameters import (
    CC,CTEA,CTEB,CTEC,EC_FACTOR,ECO,ES,F,L1,L2,ec,
    eci,eequ,eq_area,fcm,grade_values,h,sigma,strength,
)
from Process.theoretical import (
    BETA_SC,C_0,C_H,C_RH,C_c,C_fcm,C_t,C_t0,FCM0,H0,ME_E,ME_cc,NS_RH,NS_s,NS_sRH,RH0,S,T0,T1,TS,
    age_days,floor_date,creep,eci_t,elastic,loading_age_for_creep,eps_creep,eps_cs0,eps_s_fcm,eps_shrinkage,pour_day,shrinkage,stress_inc,to_date,total_load,total_ts,
)

def fixed_number(parameters, name, default):
    if name not in parameters or parameters[name] is None or parameters[name] == "":
        return default
    return float(parameters[name])

def common_variables():
    return {
        "F": F,
        "FCM0": FCM0,
        "BETA_SC": BETA_SC,
        "ES": ES,
        "ECO": ECO,
        "S": S,
        "RH0": RH0,
        "T0": T0,
        "TS": TS,
        "T1": T1,
        "H0": H0,
        "EC_FACTOR": EC_FACTOR,
    }

def opening_pair(readings):
    if len(readings) > 0:
        first_strain, first_temp = row_averages(readings[0])
    else:
        first_strain = 0.0
        first_temp = 0.0
    if len(readings) > 1:
        second_strain, second_temp = row_averages(readings[1])
    else:
        second_strain = first_strain
        second_temp = first_temp
    return first_strain, first_temp, second_strain, second_temp

def row_averages(reading):
    strain = avg_strain(float(reading["bot_strain"]), float(reading["top_strain"]))
    temp = avg_temp(float(reading["bot_temp"]), float(reading["top_temp"]))
    return strain, temp

def measured_rows_3l(readings, cs, ct, ctea, cteb, ctec, l1, l2, cc, t_wavelength, temp, temperature):
    first_strain, first_temp, _second_strain, _second_temp = opening_pair(readings)
    rows = []
    for index, reading in enumerate(readings):
        row_number = index + 1
        strain, temp_avg = row_averages(reading)
        chg_strain = change_strain(row_number, strain, first_strain)
        chg_temp = change_temp(row_number, temp_avg, first_temp)
        term = ct_term(ct, cc, chg_temp)
        measured = measured_3l(row_number, cs, cc, chg_strain, term, ctea, cteb, l1, ctec, l2)
        temp_c = temp_c_3l(ct, temp_avg, t_wavelength, cc, temp, temperature)
        rows.append({
            "item": reading["sensor_measurement"],
            "avg_strain": strain,
            "avg_temp": temp_avg,
            "chg_strain": chg_strain,
            "chg_temp": chg_temp,
            "temp_c": temp_c,
            "measured": measured,
        })
    return rows

def measured_rows_atg(readings, ks, kst_value, temp_fbg, temp_kt):
    first_strain, first_temp, second_strain, second_temp = opening_pair(readings)
    rows = []
    for index, reading in enumerate(readings):
        row_number = index + 1
        strain, temp_avg = row_averages(reading)
        chg_strain = change_strain(row_number, strain, first_strain)
        chg_temp = change_temp(row_number, temp_avg, first_temp)
        base_strain = base_reading(row_number, strain, second_strain)
        base_temp = base_reading(row_number, temp_avg, second_temp)
        measured = measured_atg(strain, base_strain, temp_avg, base_temp, kst_value, ks)
        temp_c = temp_c_atg(temp_avg, temp_fbg, temp_kt)
        rows.append({
            "item": reading["sensor_measurement"],
            "avg_strain": strain,
            "avg_temp": temp_avg,
            "chg_strain": chg_strain,
            "chg_temp": chg_temp,
            "temp_c": temp_c,
            "measured": measured,
        })
    return rows

def shrinkage_terms(days, fcm_value, rh, h_value):
    eps_s_fcm_value = eps_s_fcm(fcm_value, h_value)
    ns_srh = NS_sRH(rh, h_value, fcm_value)
    ns_rh = NS_RH(ns_srh)
    eps_cs0_value = eps_cs0(eps_s_fcm_value, ns_rh)
    ns_s = NS_s(days, h_value, fcm_value)
    eps_shrinkage_value = eps_shrinkage(eps_cs0_value, ns_s)
    return {
        "eps_cs0": eps_cs0_value,
        "eps_s_fcm": eps_s_fcm_value,
        "NS_sRH": ns_srh,
        "NS_RH": ns_rh,
        "NS_s": ns_s,
        "eps_shrinkage": eps_shrinkage_value,
    }

def creep_terms(days, loading_age, fcm_value, rh, h_value):
    used_age = loading_age_for_creep(loading_age)
    c_rh = C_RH(rh, h_value, fcm_value)
    c_fcm = C_fcm(fcm_value, h_value)
    c_t0 = C_t0(used_age)
    c_0 = C_0(c_rh, c_fcm, c_t0)
    c_h = C_H(rh, h_value, fcm_value)
    if days is not None and used_age is not None and days < used_age:
        c_c = 0.0
        c_t = 0.0
    else:
        c_c = C_c(days, used_age, c_h)
        c_t = C_t(c_0, c_c)
    return {
        "C_t": c_t,
        "C_0": c_0,
        "C_RH": c_rh,
        "C_fcm": c_fcm,
        "C_t0": c_t0,
        "C_c": c_c,
        "C_H": c_h,
    }

def floor_stages(stress_dates, poured, base_floor, mid_floor, roof_floor, sigma_base, sigma_mid, sigma_roof):
    labeled = [
        (floor_date(stress_dates, base_floor), sigma_base),
        (floor_date(stress_dates, mid_floor), sigma_mid),
        (floor_date(stress_dates, roof_floor), sigma_roof),
    ]
    labeled.sort(key=lambda item: item[0])
    stages = []
    previous = 0.0
    for stage_date, sigma_value in labeled:
        stages.append({
            "date": stage_date,
            "sigma": sigma_value,
            "increment": sigma_value - previous,
            "loading_age": age_days(stage_date, poured),
        })
        previous = sigma_value
    return stages

def stages_reached(day, stages):
    current = to_date(day)
    reached = []
    for stage in stages:
        if stage["date"] <= current:
            reached.append(stage)
    return reached

def creep_part(increment, days, loading_age, eci_value, fcm_value, rh, h_value):
    terms = creep_terms(days, loading_age, fcm_value, rh, h_value)
    used_age = loading_age_for_creep(loading_age)
    loaded_modulus = eci_t(ME_E(ME_cc(used_age), eci_value), eci_value)
    return eps_creep(increment, loaded_modulus, terms["C_t"])

def creep_at(day, days, stages, eci_value, fcm_value, rh, h_value):
    reached = stages_reached(day, stages)
    if len(reached) == 0:
        return 0.0
    total = 0.0
    for stage in reached:
        part = creep_part(
            stage["increment"], days, stage["loading_age"], eci_value, fcm_value, rh, h_value,
        )
        if part is None:
            return None
        total = total + part
    return total

def stress_at(day, stages):
    reached = stages_reached(day, stages)
    if len(reached) == 0:
        return 0.0
    return reached[-1]["sigma"]

def stress_tables(stress_dates, poured, load, ec_value, eci_value, fcm_value, rh, h_value, stages, base_loading_age, base_date):
    modulus_rows = []
    shrinkage_rows = []
    creep_rows = []
    for index, stress_date in enumerate(stress_dates):
        row_number = index + 1
        days = age_days(stress_date, poured)

        me_cc = ME_cc(days)
        me_e = ME_E(me_cc, eci_value)
        eci_t_value = eci_t(me_e, eci_value)
        shrink = shrinkage_terms(days, fcm_value, rh, h_value)
        coeffs = creep_terms(days, base_loading_age, fcm_value, rh, h_value)
        if to_date(stress_date) < base_date:
            eps_creep_value = 0.0
        else:
            eps_creep_value = creep_at(
                stress_date, days, stages, eci_value, fcm_value, rh, h_value,
            )

        modulus_rows.append({
            "row": row_number,
            "stress_date": to_date(stress_date).strftime("%d-%m-%Y"),
            "age": days,
            "total_load": total_load(load, row_number),
            "stress_inc": stress_inc(load),
            "ec": ec_value,
            "eci_t": eci_t_value,
            "eci": eci_value,
            "ME_E": me_e,
            "ME_cc": me_cc,
        })
        shrinkage_rows.append({
            "eps_cs0": shrink["eps_cs0"],
            "eps_s_fcm": shrink["eps_s_fcm"],
            "NS_sRH": shrink["NS_sRH"],
            "NS_RH": shrink["NS_RH"],
            "NS_s": shrink["NS_s"],
            "eps_shrinkage": shrink["eps_shrinkage"],
        })
        creep_rows.append({
            "row": row_number,
            "age": days,
            "C_t": coeffs["C_t"],
            "C_0": coeffs["C_0"],
            "C_RH": coeffs["C_RH"],
            "C_fcm": coeffs["C_fcm"],
            "C_t0": coeffs["C_t0"],
            "C_c": coeffs["C_c"],
            "C_H": coeffs["C_H"],
            "eps_creep": eps_creep_value,
        })
    return modulus_rows, shrinkage_rows, creep_rows

def strain_rows(readings, measured_rows, poured, stages, eequ_value, eci_value, fcm_value, rh, h_value):
    rows = []
    for index, reading in enumerate(readings):
        date_text = to_date(reading["date"]).strftime("%d-%m-%Y")
        days = age_days(reading["date"], poured)
        shrink_terms = shrinkage_terms(days, fcm_value, rh, h_value)
        shrink = shrinkage(shrink_terms["eps_shrinkage"])
        creep_value = creep(creep_at(
            reading["date"], days, stages, eci_value, fcm_value, rh, h_value,
        ))
        elastic_value = elastic(stress_at(reading["date"], stages), eequ_value)
        total = total_ts(shrink, creep_value, elastic_value)
        rows.append({
            "item": reading["sensor_measurement"],
            "date": date_text,
            "measured": measured_rows[index]["measured"],
            "shrinkage": shrink,
            "creep": creep_value,
            "elastic": elastic_value,
            "total_ts": total,
        })
    return rows

def build_result(record):
    parameters = record["parameters"]
    readings = record["readings"]
    stress_dates = record["stress_dates"]

    sfc = float(parameters["sfc"])
    rh = float(parameters["rh"])
    ac = float(parameters["ac"])
    ar = float(parameters["ar"])
    u = float(parameters["u"])
    load = float(parameters["load"])
    base_floor = float(parameters["base_floor"])
    mid_floor = float(parameters["mid_floor"])
    roof_floor = float(parameters["roof_floor"])

    fck, ec_grade, grade = grade_values(parameters["concrete_grade"])
    fcm_value = fcm(fck)
    eequ_value = eequ(fck, ac, sfc, ar)
    h_value = h(ac, u)
    eci_value = eci(fck)
    ec_value = ec(eci_value)
    strength_value = strength(ec_grade, ac, ar)
    eq_area_value = eq_area(strength_value, ec_grade)
    sigma_base = sigma(load, base_floor)
    sigma_mid = sigma(load, mid_floor)
    sigma_roof = sigma(load, roof_floor)
    base_stress_date = floor_date(stress_dates, base_floor).strftime("%d-%m-%Y")
    mid_stress_date = floor_date(stress_dates, mid_floor).strftime("%d-%m-%Y")
    roof_stress_date = floor_date(stress_dates, roof_floor).strftime("%d-%m-%Y")

    report = {
        "grade": grade,
        "fck": fck,
        "fcm": fcm_value,
        "ec": ec_grade,
        "eequ": eequ_value,
        "h": h_value,
        "strength": strength_value,
        "eq_area": eq_area_value,
        "sigma_base": sigma_base,
        "base_stress_date": base_stress_date,
        "sigma_mid": sigma_mid,
        "mid_stress_date": mid_stress_date,
        "sigma_roof": sigma_roof,
        "roof_stress_date": roof_stress_date,
        "base_floor": int(base_floor),
        "mid_floor": int(mid_floor),
        "roof_floor": int(roof_floor),
        "eci": eci_value,
    }
    variables = common_variables()

    if record["sensor_type"] == "3L":
        cs = float(parameters["cs"])
        ct = float(parameters["ct"])
        ctea = fixed_number(parameters, "ctea", CTEA)
        cteb = fixed_number(parameters, "cteb", CTEB)
        ctec = fixed_number(parameters, "ctec", CTEC)
        l1 = fixed_number(parameters, "l1", L1)
        l2 = fixed_number(parameters, "l2", L2)
        cc = fixed_number(parameters, "cc", CC)
        t_wavelength = float(parameters["t_wavelength"])
        temperature = float(parameters["temperature"])
        temp = float(parameters["temp"])
        report["cs"] = cs
        report["ct"] = ct
        report["ctea"] = ctea
        report["cteb"] = cteb
        report["ctec"] = ctec
        report["l1"] = l1
        report["l2"] = l2
        report["cc"] = cc
        variables["CTEA"] = CTEA
        variables["CTEB"] = CTEB
        variables["CTEC"] = CTEC
        variables["L1"] = L1
        variables["L2"] = L2
        variables["CC"] = CC
        measured_rows = measured_rows_3l(
            readings, cs, ct, ctea, cteb, ctec, l1, l2, cc, t_wavelength, temp, temperature,
        )
    else:
        ks = float(parameters["ks"])
        ktt = float(parameters["ktt"])
        kts = float(parameters["kts"])
        kst_value = kst(kts, ktt)
        temp_fbg = fixed_number(parameters, "Temp-FBG", 0.0)
        temp_kt = float(parameters["Temp-FBG1"])
        report["ks"] = ks
        report["ktt"] = ktt
        report["kts"] = kts
        report["kst"] = kst_value
        report["temp_fbg"] = temp_fbg
        report["temp_kt"] = temp_kt
        measured_rows = measured_rows_atg(readings, ks, kst_value, temp_fbg, temp_kt)

    poured = pour_day(parameters["t0"], stress_dates)
    stages = floor_stages(
        stress_dates, poured, base_floor, mid_floor, roof_floor,
        sigma_base, sigma_mid, sigma_roof,
    )
    base_date = floor_date(stress_dates, base_floor)
    base_loading_age = age_days(base_date, poured)
    modulus_rows, shrinkage_rows, creep_rows = stress_tables(
        stress_dates, poured, load, ec_value, eci_value, fcm_value, rh, h_value,
        stages, base_loading_age, base_date,
    )
    output_rows = strain_rows(
        readings, measured_rows, poured, stages, eequ_value, eci_value, fcm_value, rh, h_value,
    )
    return {
        "parameters": report,
        "functions": [
            "parameter_values",
            "measured_strain",
            "modulus_row",
            "shrinkage_row",
            "creep_row",
            "output_row",
        ],
        "variables": variables,
        "measured_strain": measured_rows,
        "modulus": modulus_rows,
        "shrinkage": shrinkage_rows,
        "creep": creep_rows,
        "output": output_rows,
    }