"""Deseuri medicale periculoase (CPV 90524x), spitale publice — set refacut, VERSIUNEA 6 (2026-09-23).
Surse: tenders.db (randuri brute), data/ted_parsed_9052.json (XML TED de pe disc: atribuire eForms/F03, participare eForms-CN/F02,
erate F14), OpenTender main.csv 2020-2024. Iesire: outreach_sep2026/pressone_v6/. DB'ye yazmaz. Regulile sunt descrise in
metodologie_v6.txt; verificarile automate in verificari.txt."""
import os, sys, csv, json, os, re, sqlite3, datetime, collections, glob, calendar, unicodedata
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument("--niche", default="deseuri_medicale"); _ap.add_argument("--cpv", default="90524%")
_ap.add_argument("--cpv-exclude", default="", help="prefixe CPV excluse, separate prin virgula (ex. 336)")
_ap.add_argument("--cpv-check", default="90524", help="prefix asteptat pentru verificarea 'toate CPV'")
_ap.add_argument("--parsed", default="/opt/ted-engine/data/ted_parsed_9052.json")
_ap.add_argument("--out", default="/opt/ted-engine/outreach_sep2026/pressone_v6")
_ap.add_argument("--today", default=None); _A = _ap.parse_args()
OUT = _A.out; os.makedirs(OUT, exist_ok=True)
DB = "/opt/ted-engine/tenders.db"
TODAY = datetime.date.fromisoformat(_A.today) if _A.today else datetime.date.today()
H12 = datetime.date(TODAY.year + 1, TODAY.month, TODAY.day)
CPV_EXCL = tuple(x.strip() for x in _A.cpv_exclude.split(",") if x.strip())
csv.field_size_limit(10**9)

# ---------- utilitare ----------
def strip_diac(s): return "".join(ch for ch in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(ch))
def norm_id(tid):
    t = tid.split(":award")[0]
    if t.startswith("ot:"): t = t[3:]
    m = re.fullmatch(r"(\d{4})/S\s*\d+-(\d+)", t)
    if m: return f"{int(m.group(2))}-{m.group(1)}"
    m = re.fullmatch(r"0*(\d{5,7})-(\d{4})", t)
    if m: return f"{int(m.group(1))}-{m.group(2)}"
    return t
def is_ted_id(nid): return bool(re.fullmatch(r"\d+-\d{4}", nid))
def add_months(d, m):
    if abs(m - round(m)) > 0.01: return d + datetime.timedelta(days=int(round(m * 30.44)))
    m = int(round(m)); y, mo = d.year + (d.month - 1 + m) // 12, (d.month - 1 + m) % 12 + 1
    return datetime.date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))
def wnorm(x):
    x = re.sub(r"\b(S\.?C\.?|S\.?R\.?L\.?|S\.?A\.?|SRL|SA|ROMANIA)\b", "", strip_diac(x).upper())
    return re.sub(r"\W+", "", x)
def hnorm(x): return re.sub(r"\W+", "", strip_diac(x).upper())
def tnorm(t): return re.sub(r"[^A-Z0-9]+", "", strip_diac(t or "").upper())
def dparse(s):
    try: return datetime.date.fromisoformat(str(s)[:10])
    except Exception: return None
def months_of(d, u):
    u = (u or "").upper()
    if u.startswith("MON"): return d
    if u.startswith("DAY"): return round(d / 30.44, 1)
    if u.startswith("YEAR"): return d * 12
    if u.startswith("WEEK"): return round(d * 7 / 30.44, 1)
    return None

# ---------- surse ----------
P = json.load(open(_A.parsed))
ot = {}
for f in sorted(glob.glob("/opt/ted-engine/data/opentender_cache/opentender_ro_*/*/main.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        k = norm_id(r.get("tender_id", ""))
        if k: ot[k] = {"days": r.get("tender_contractPeriod_durationInDays") or "", "end": (r.get("tender_contractPeriod_endDate") or "")[:10],
                       "value": r.get("tender_value_amount") or "", "method": r.get("tender_procurementMethodDetails") or r.get("tender_procurementMethod") or "",
                       "title": r.get("tender_title") or "", "award_end": (r.get("tender_awardPeriod_endDate") or "")[:10]}
print("opentender:", len(ot), "| ted parsed:", len(P))

# ---------- clasificare autoritate (fara diacritice) ----------
HOSP = re.compile(r"SPITAL|INSTITUT|CLINIC|SANATOR|MATERNIT|POLICLINIC|ADMINISTRATIA SPITALELOR", re.I)
# unitati militare cu profil de spital (spitale militare de urgenta, INMAS, sanatoriul Baltatesti); verificate dupa datele de contact din anunturi
MIL_HOSP = re.compile(r"SPITAL.*MILITAR|MILITAR.*SPITAL|MEDICINA AERONAUTICA|U\.?M\.?\s?0?2175\b|U\.?M\.?\s?0?2534\b|U\.?M\.?\s?0?2460\b|U\.?M\.?\s?0?929\b|UNITATEA MILITARA 0?521\b|U\.?M\.?\s?0?521\b|U\.?M\.?\s?0?2454\b|U\.?M\.?\s?0?2497\b|U\.?M\.?\s?0?2558\b|U\.?M\.?\s?0?2489\b|U\.?M\.?\s?0?2417\b|U\.?M\.?\s?0?2275\b|U\.?M\.?\s?0?2587\b|UNITATEA MILITARA 0?(2497|2558|2489|2417|2275|2587)\b", re.I)
PRIV = re.compile(r"\bS\.?\s?R\.?\s?L\.?\b|\bS\.?\s?A\.?\b(?!\w)|\bSRL\b", re.I)
RESEARCH = re.compile(r"CERCETARE|TRANSFUZIE|CONTROLUL PRODUSELOR BIOLOGICE|PETRU PONI|FIZICA|LASER|SILVICULTUR|ECOLOGIE INDUSTRIALA|BIOLOGIE SI PATOLOGIE CELULARA|SUDURA", re.I)
NONH = re.compile(r"ASISTENTA SOCIALA|PROTECTIA COPILULUI|DSVSA|SANITAR VETERINAR|PENITENCIAR|POLITI|SANATATE PUBLICA|MEDICINA LEGALA|OMV|PETROM|PRIMARIA|MUNICIPIUL |SECTORUL |CONSILIUL JUDETEAN|UNIVERSITATEA DE MEDICINA|MONETARIA|SERVICIUL DE AMBULANTA|REGIA AUTONOMA", re.I)
def classify(name):
    n = strip_diac(name or "")
    if MIL_HOSP.search(n): return "spital", "unitate militara cu profil de spital"
    if re.search(r"PENITENCIAR", n, re.I) and re.search(r"SPITAL", n, re.I): return "spital", "spital penitenciar"
    if NONH.search(n): return "exclus", "autoritate non-spital"
    if PRIV.search(n): return "exclus", "entitate privata (SRL/SA)"
    if RESEARCH.search(n): return "exclus", "institut de cercetare / fara paturi de spital"
    if re.search(r"AMBULATORIU", n, re.I): return "exclus", "centru medical ambulatoriu (fara paturi)"
    if re.search(r"MILITAR|\bU\.?M\.?\s?\d|UNITATEA MILITARA", n, re.I): return "exclus", "unitate militara fara profil de spital"
    if HOSP.search(n): return "spital", ""
    return "exclus", "autoritate non-spital"

# ---------- 1. randuri brute -> anunturi (id normalizat) ----------
c = sqlite3.connect(DB)
rows = c.execute("""select tender_id, hospital_name, winner_name, value_ron, value_type, award_date, cpv_primary
                    from contract_awards where cpv_primary like ? order by award_date, tender_id""", (_A.cpv,)).fetchall()
rows = [r for r in rows if not (CPV_EXCL and str(r[6] or "").startswith(CPV_EXCL))]
print("randuri brute:", len(rows))
trace = []   # (id_brut, id_normalizat, id_final, relatie)
ann = collections.OrderedDict()  # nid -> anunt
excl_raw = []
def add_trace(raw, nid, final, rel): trace.append((raw, nid, final, rel))
for tid, h, w, v, vt, ad, cpv in rows:
    nid = norm_id(tid)
    a = ann.setdefault(nid, {"nid": nid, "hospital": h, "raw": [], "db_winners": [], "db_vals_ted": [], "db_vals_ot": [], "vt": vt, "db_award": (ad or "")[:10], "cpv": cpv, "srcs": set()})
    a["raw"].append(tid); a["srcs"].add("TED" if not tid.startswith("ot:") else "OT")
    if "ADJUDECARE" not in (w or "").upper():
        for part in re.split(r"\s+/\s+", (w or "").strip()):
            part = re.sub(r"\s+", " ", part).strip()
            if part and wnorm(part) not in {wnorm(x) for x in a["db_winners"]}: a["db_winners"].append(part)
        if v: (a["db_vals_ted"] if not tid.startswith("ot:") else a["db_vals_ot"]).append(float(v))
    if not a["db_award"] or ((ad or "")[:10] and (ad or "")[:10] < a["db_award"]): a["db_award"] = (ad or "")[:10]
print("anunturi (id normalizat):", len(ann))

# ---------- 2. imbogatire din XML / OT ----------
for nid, a in ann.items():
    p = P.get(nid) if is_ted_id(nid) else None
    o = ot.get(nid) or {}
    a["p"] = p; a["fmt"] = (p or {}).get("fmt") or ("sicap" if not is_ted_id(nid) else "ted_fara_xml")
    a["title"] = (p or {}).get("title") or o.get("title") or ""
    a["winners"] = [] if (p or {}).get("fmt") in ("legacy_corr", "legacy_cn") or str((p or {}).get("notice_type") or "").startswith("cn") or (p and p.get("no_winner")) else (list((p or {}).get("winners") or []) or list(a["db_winners"]))
    if not is_ted_id(nid) and o.get("award_end") and (not a["db_award"] or o["award_end"] < a["db_award"]):
        a["db_award"] = o["award_end"]; a["date_note_sicap"] = "data = sfarsitul perioadei de atribuire din SICAP/OpenTender"
    a["contract_dates"] = list((p or {}).get("contract_dates") or [])
    a["no_winner"] = bool((p or {}).get("no_winner"))
    a["folder"] = (p or {}).get("folder"); a["prior"] = (p or {}).get("prior")
    a["notice_type"] = (p or {}).get("notice_type") or ("F03" if a["fmt"] == "legacy_can" else "F02" if a["fmt"] == "legacy_cn" else "")
    a["is_award_notice"] = a["fmt"] == "legacy_can" or (a["fmt"] == "eforms" and str(a["notice_type"]).startswith("can"))
    a["is_corr"] = a["fmt"] == "legacy_corr"
    # F03 -> anuntul de participare (F02) din lantul de referinte (poate trece printr-un F03 anterior); XML-ul e pe disc
    f02 = None; prior_chain = []
    if p and p.get("fmt") == "legacy_can":
        q = p; depth = 0
        while q and q.get("prior") and depth < 4:
            prior_chain.append(q["prior"]); q = P.get(q["prior"]); depth += 1
            if q and q.get("fmt") == "legacy_cn": f02 = q; break
    a["f02"] = f02; a["prior_chain"] = prior_chain
    a["negociat"] = bool(re.search(r"NEGOCIER", strip_diac(o.get("method") or "").upper())) or a["vt"] == "negotiated" or bool(re.search(r"NEGOCIERE", strip_diac(a["title"]).upper()))
    # valori: atribuita numai din XML pentru anunturile TED; din inregistrarea SICAP (valorile OT pe atribuire) altfel
    a["awarded"] = None; a["awarded_src"] = ""; a["fw_max"] = None; a["fw_max_src"] = ""; a["fw_max_est"] = None
    if p and p.get("fmt") == "eforms":
        if p.get("total_amount"): a["awarded"], a["awarded_src"] = p["total_amount"], "TED eForms (valoarea totala a rezultatului)"
        if p.get("fw_max_notice"): a["fw_max"], a["fw_max_src"] = p["fw_max_notice"], "TED eForms BT-118 (valoarea maxima a acordului)"
        elif p.get("fw_max_lots_sum"): a["fw_max"], a["fw_max_src"] = p["fw_max_lots_sum"], "TED eForms (suma valorilor maxime pe loturi)"
        elif p.get("estimated"): a["fw_max"], a["fw_max_src"] = p["estimated"], "TED eForms (valoare estimata)"
        a["fw_max_est"] = p.get("fw_max_est")
    elif p and p.get("fmt") == "legacy_can":
        vt_ = [cc["val_total"] for cc in p.get("contracts", []) if cc.get("val_total")]
        if p.get("val_total_notice"): a["awarded"], a["awarded_src"] = p["val_total_notice"], "TED F03 (II.1.7 valoarea totala a achizitiei)"
        elif vt_: a["awarded"], a["awarded_src"] = sum(vt_), "TED F03 (suma VAL_TOTAL pe contracte)"
        est = [v for v in (p.get("estimated"), p.get("estimated_notice"), (f02 or {}).get("estimated")) if v]
        if est: a["fw_max"], a["fw_max_src"] = max(est), ("TED F02 (valoare estimata totala)" if f02 and (f02.get("estimated") or 0) >= max(est) else "TED F03 (valoare estimata totala)")
    elif p and p.get("fmt") == "legacy_cn":
        if p.get("estimated"): a["fw_max"], a["fw_max_src"] = p["estimated"], "TED F02 (valoare estimata totala)"
    if a["awarded"] is None and not is_ted_id(nid):
        vs = a["db_vals_ot"]
        if vs:
            if len(set(round(x) for x in vs)) == 1: a["awarded"] = vs[0]; a["awarded_note"] = (f"{len(vs)} randuri SICAP cu valoare identica (posibil loturi egale sau acord cu mai multi castigatori); valoarea numarata o singura data" if len(vs) > 1 else "")
            elif len(vs) >= 3 and abs(max(vs) - (sum(vs) - max(vs))) / max(vs) <= 0.01: a["awarded"] = max(vs); a["awarded_note"] = "inregistrarea SICAP contine un rand total si randuri pe loturi; totalul o singura data"
            else: a["awarded"] = sum(vs); a["awarded_note"] = "suma loturi" if len(vs) > 1 else ""
            a["awarded_src"] = "SICAP/OpenTender (valori pe atribuire)"
    if a["fw_max"] is None and o.get("value"):
        try:
            fv = float(o["value"])
            if fv > 0 and not (a["awarded"] and fv >= 20 * a["awarded"]): a["fw_max"], a["fw_max_src"] = fv, "SICAP/OpenTender (valoare procedura)"
            elif fv > 0: a["ot_value_ignored"] = f"valoarea procedurii din SICAP/OpenTender ({round(fv):,} RON) ignorata: de peste 20 de ori valoarea atribuita (probabil eroare de unitate)".replace(",", ".")
        except Exception: pass
    # acord-cadru?
    a["fw"] = bool((p or {}).get("fw")) or bool((f02 or {}).get("fw")) or a["vt"] == "framework" or ("cadru" in (o.get("method") or "").lower()) or bool(re.search(r"ACORD[\s-]*CADRU", strip_diac(a["title"]).upper()))
    # durata: eForms > F02 (din lant) > OT
    a["dur"] = None; a["dur_src"] = ""; a["end_pub"] = None
    src_dur = p if (p and p.get("duration")) else (f02 if (f02 and f02.get("duration")) else None)
    if src_dur and months_of(src_dur["duration"], src_dur.get("unit")):
        a["dur"] = months_of(src_dur["duration"], src_dur.get("unit")); a["dur_src"] = "TED eForms (durata publicata)" if src_dur.get("fmt") == "eforms" else "TED F02 (durata publicata)"
    elif p and p.get("planned_end"): a["end_pub"] = p["planned_end"]; a["dur_src"] = "TED eForms (data incheierii publicata)"
    elif (p and p.get("end")) or (f02 and f02.get("end")): a["end_pub"] = (p.get("end") if p and p.get("end") else f02["end"]); a["dur_src"] = "TED F02 (data incheierii publicata)"
    elif o.get("end"): a["end_pub"] = o["end"]; a["dur_src"] = "SICAP/OpenTender (data incheierii publicata)"
    elif o.get("days"):
        try: a["dur"] = round(int(float(o["days"])) / 30.44, 1); a["dur_src"] = "SICAP/OpenTender (durata publicata, zile)"
        except Exception: pass

# ---------- 3. excluderi la nivel de anunt ----------
proc_in = collections.OrderedDict()
for nid, a in ann.items():
    kind, why = classify(a["hospital"])
    if kind == "exclus":
        for r in a["raw"]: add_trace(r, nid, "", "exclus: " + why)
        excl_raw.append((nid, a["hospital"], " / ".join(a["winners"]), a.get("awarded") or a.get("fw_max"), a["db_award"], why)); continue
    a["hosp_note"] = why
    if re.search(r"MENAJER", strip_diac(a["title"]).upper()) and not re.search(r"MEDICAL|PERICUL|SPITAL", strip_diac(a["title"]).upper()):
        for r in a["raw"]: add_trace(r, nid, "", "exclus: deseuri menajere dupa titlu")
        excl_raw.append((nid, a["hospital"], " / ".join(a["winners"]), a.get("awarded") or a.get("fw_max"), a["db_award"], f"deseuri menajere dupa titlu ('{a['title'][:60]}')")); continue
    if a["no_winner"] and not a["winners"]:
        for r in a["raw"]: add_trace(r, nid, "", "exclus: procedura anulata / fara castigator (XML TED)")
        excl_raw.append((nid, a["hospital"], "", a.get("fw_max"), a["db_award"], "procedura anulata / fara castigator (confirmat in XML TED)")); continue
    if not a["winners"] and a["is_award_notice"]:
        for r in a["raw"]: add_trace(r, nid, "", "exclus: castigator neidentificat in anuntul de atribuire")
        excl_raw.append((nid, a["hospital"], "", a.get("fw_max"), a["db_award"], "castigator neidentificat in anuntul de atribuire (nici XML, nici SICAP)")); continue
    proc_in[nid] = a
print("anunturi retinute:", len(proc_in), "| excluse:", len(excl_raw))

# ---------- 4. gruparea anunturilor in proceduri ----------
def pkey(a):
    if a["folder"]: return "F:" + a["folder"]
    if a["fmt"] == "legacy_can" and a["prior_chain"]:
        term = next((x for x in a["prior_chain"] if (P.get(x) or {}).get("fmt") == "legacy_cn"), a["prior_chain"][-1])
        return "P:" + term
    if a["fmt"] == "legacy_cn": return "P:" + a["nid"]
    if a["fmt"] == "legacy_corr": return ("P:" + a["prior"]) if a["prior"] else ("P:" + a["nid"])
    if a["fmt"] == "ted_fara_xml": return "P:" + a["nid"]   # id TED provenit din OT, probabil anunt de participare
    return None
groups = collections.OrderedDict()  # key -> list of anunturi
loose = []
for a in proc_in.values():
    k = pkey(a)
    if k:
        groups.setdefault(k, []).append(a)
        a["join"] = "acelasi ContractFolderID" if k.startswith("F:") else ("erata (F14) la anuntul de participare" if a["fmt"] == "legacy_corr" else "acelasi anunt de participare (F02)")
    else: loose.append(a)
def ttoks(t): return {w for w in re.split(r"[^A-Z0-9]+", strip_diac(t or "").upper()) if len(w) > 3}
def title_sim(t1, t2):
    A, B = ttoks(t1), ttoks(t2)
    if not A or not B: return 1.0
    return len(A & B) / len(A | B)
# inregistrari SICAP fara identificator TED: se leaga de un anunt TED al aceleiasi proceduri numai daca NU sunt negocieri
def attach_loose(a):
    """acelasi spital + CPV si: (a) anuntul TED este de participare (fara castigatori pe el) si data SICAP = data lui +/-3 zile;
    (b) aceiasi castigatori + data +/-14 zile fata de o data de contract din anuntul TED + titlu compatibil."""
    if a["negociat"]: return None
    da = dparse(a["db_award"])
    for k, lst in groups.items():
        for b in lst:
            if hnorm(b["hospital"]) != hnorm(a["hospital"]) or str(b["cpv"])[:5] != str(a["cpv"])[:5]: continue
            if b.get("negociat"): continue
            b_is_cn = str(b.get("notice_type") or "").startswith("cn") or b["fmt"] == "legacy_cn"
            if b_is_cn or not b["winners"]:
                db_ = dparse(b["db_award"]); sim = title_sim(a["title"], b["title"])
                if da and db_ and ((abs((da - db_).days) <= 3 and sim >= 0.3) or (abs((da - db_).days) <= 45 and sim >= 0.7)): return k
            elif a["winners"]:
                if {wnorm(x) for x in a["winners"]} != {wnorm(x) for x in b["winners"]}: continue
                dates = [dparse(d) for d in b["contract_dates"]] or [dparse(b["db_award"])]
                if da and any(d and abs((da - d).days) <= 14 for d in dates) and title_sim(a["title"], b["title"]) >= 0.3: return k
    return None
_bucket = collections.defaultdict(list)
for k, lst in groups.items():
    for b in lst: _bucket[(hnorm(b["hospital"]), str(b["cpv"])[:5])].append((k, b))
def attach_loose(a):
    if a["negociat"]: return None
    da = dparse(a["db_award"])
    for k, b in _bucket.get((hnorm(a["hospital"]), str(a["cpv"])[:5]), []):
        if b.get("negociat"): continue
        b_is_cn = str(b.get("notice_type") or "").startswith("cn") or b["fmt"] == "legacy_cn"
        if b_is_cn or not b["winners"]:
            db_ = dparse(b["db_award"]); sim = title_sim(a["title"], b["title"])
            if da and db_ and ((abs((da - db_).days) <= 3 and sim >= 0.3) or (abs((da - db_).days) <= 45 and sim >= 0.7)): return k
        elif a["winners"]:
            if {wnorm(x) for x in a["winners"]} != {wnorm(x) for x in b["winners"]}: continue
            dates = [dparse(d) for d in b["contract_dates"]] or [dparse(b["db_award"])]
            if da and any(d and abs((da - d).days) <= 14 for d in dates) and title_sim(a["title"], b["title"]) >= 0.3: return k
    return None
for a in loose:
    k = attach_loose(a)
    if k: groups[k].append(a); a["join"] = "inregistrare SICAP a aceleiasi proceduri (data, castigatori, titlu)"
    else: groups["N:" + a["nid"]] = [a]; a["join"] = "acelasi anunt"
# duplicate SICAP (inclusiv negocieri): acelasi spital, aceiasi castigatori, aceeasi zi, aceeasi valoare (+/-1%), acelasi titlu
_nb = collections.defaultdict(list)
for k in groups:
    if k.startswith("N:"): a0 = groups[k][0]; _nb[(hnorm(a0["hospital"]), a0["db_award"])].append(k)
for nkeys in _nb.values():
  for i1, k1 in enumerate(nkeys):
    if k1 not in groups: continue
    a1 = groups[k1][0]
    for k2 in nkeys[i1 + 1:]:
        if k2 not in groups: continue
        a2 = groups[k2][0]
        if {wnorm(x) for x in a1["winners"]} != {wnorm(x) for x in a2["winners"]}: continue
        v1, v2 = a1.get("awarded") or a1.get("fw_max"), a2.get("awarded") or a2.get("fw_max")
        if not (v1 and v2 and abs(v1 - v2) / max(v1, v2) <= 0.01): continue
        if tnorm(a1["title"]) != tnorm(a2["title"]): continue
        groups[k1].append(a2); a2["join"] = "inregistrare SICAP duplicata (aceeasi zi, valoare, titlu)"; groups.pop(k2)
# a doua trecere intre grupuri TED: aceeasi procedura publicata in format vechi (P:) si eForms (F:) etc.; negocierile SICAP nu se unesc
def gdate(lst):
    ds = [d for b in lst for d in b["contract_dates"]] or [b["db_award"] for b in lst if b["db_award"]]
    return min(ds) if ds else None
def gwin(lst): return {wnorm(x) for b in lst for x in b["winners"]}
def gted(lst): return any(is_ted_id(b["nid"]) for b in lst)
merged = {}
_gb = collections.defaultdict(list)
# numai pe spital (toate ortografiile membrilor): CPV-ul si numele din anuntul de participare pot diferi de cele din atribuire
for k, lst in groups.items():
    for hn in {hnorm(b["hospital"]) for b in lst}: _gb[hn].append(k)
_seen_pairs = set()
for keys in _gb.values():
  for i, k in enumerate(keys):
    if k in merged: continue
    for k2 in keys[i + 1:]:
        if k2 in merged or (k, k2) in _seen_pairs: continue
        _seen_pairs.add((k, k2))
        A, B = groups[k], groups[k2]
        if os.environ.get("DBG_PAIR") and any(b["nid"] in os.environ["DBG_PAIR"].split(",") for b in A + B):
            print("DBG", k, k2, [b["nid"] for b in A], [b["nid"] for b in B], gted(A), gted(B), [b.get("negociat") for b in A + B], gwin(A), gwin(B), gdate(A), gdate(B), file=sys.stderr)
        if not (gted(A) and gted(B)): continue
        if any(b.get("negociat") for b in A + B): continue
        if not (gwin(A) & gwin(B)): continue
        da, db_ = dparse(gdate(A)), dparse(gdate(B))
        same_w = gwin(A) == gwin(B)
        # acelasi acord-cadru publicat in format vechi (F03) si apoi in eForms: aceiasi castigatori, acelasi titlu, aceeasi valoare maxima (+/-1%), <= 18 luni
        def _fw(lst): return [v for v in (b.get("fw_max") for b in lst) if v]
        # acelasi acord republicat in eForms: aceleasi date de incheiere a contractelor (exacte) + castigatori comuni (Jaccard >= 0.5)
        _cdA, _cdB = {d for b in A for d in b["contract_dates"]}, {d for b in B for d in b["contract_dates"]}
        same_cd = bool(_cdA & _cdB) and len(gwin(A) & gwin(B)) / max(1, len(gwin(A) | gwin(B))) >= 0.5
        same_fw = same_w and tnorm(A[0]["title"]) == tnorm(B[0]["title"]) and _fw(A) and _fw(B) and abs(max(_fw(A)) - max(_fw(B))) / max(max(_fw(A)), max(_fw(B))) <= 0.01 and da and db_ and abs((da - db_).days) <= 540
        if (da and db_ and abs((da - db_).days) <= (14 if same_w else 3)) or same_fw or same_cd:
            fa, fb = {b["folder"] for b in A if b["folder"]}, {b["folder"] for b in B if b["folder"]}
            if fa and fb and fa != fb: continue   # doua foldere eForms diferite = proceduri diferite
            for b in B: b["join"] = ("acelasi acord-cadru (titlu, castigatori, valoare maxima; format vechi <-> eForms)" if same_fw else ("acelasi acord (aceleasi date de incheiere a contractelor, castigatori; format vechi <-> eForms)" if same_cd else "acelasi spital+castigatori+data (format vechi <-> eForms)"))
            groups[k].extend(B); merged[k2] = k
for k2 in merged: groups.pop(k2, None)
print("proceduri (dupa grupare):", len(groups))

# ---------- 5. consolidare: un rand per procedura ----------
def build_proc(lst):
    award_notices = [b for b in lst if b["is_award_notice"]]
    # id-ul procedurii = cel mai vechi anunt de atribuire (stabil); datele/valorile se iau din reuniunea tuturor anunturilor
    def pub_order(b):
        m = re.fullmatch(r"(\d+)-(\d{4})", b["nid"])
        return (int(m.group(2)), int(m.group(1))) if m else (9999, 0)
    head = min(lst, key=lambda b: (not b["is_award_notice"], not b["winners"], bool(b.get("no_winner")), pub_order(b), b["db_award"] or "9999", b["nid"]))
    g = {"nid": head["nid"], "members": lst, "hospital": head["hospital"], "hosp_note": next((b["hosp_note"] for b in lst if b.get("hosp_note")), ""), "cpv": head["cpv"]}
    g["winners"] = []
    for b in sorted(lst, key=lambda b: (not b["is_award_notice"], b["nid"])):
        for x in b["winners"]:
            if wnorm(x) not in {wnorm(y) for y in g["winners"]}: g["winners"].append(x)
    cds = sorted({d for b in lst for d in b["contract_dates"]})
    _yrs = [int(m.group(2)) for b in lst for m in [re.fullmatch(r"(\d+)-(\d{4})", b["nid"])] if m]
    _ymin = max(2010, (min(_yrs) - 5)) if _yrs else 2010   # doar erori evidente de tastare (ex. anul 2000); contractele publicate cu intarziere raman
    _bad = [d for d in cds if (dparse(d) and (dparse(d).year < _ymin or dparse(d) > TODAY + datetime.timedelta(days=30)))]
    cds = [d for d in cds if d not in _bad]
    g["contract_dates"] = cds
    g["date_note_bad"] = ("data/date de contract implauzibile ignorate: " + ", ".join(_bad)) if _bad else ""
    g["award"] = cds[0] if cds else min(b["db_award"] for b in lst if b["db_award"])
    g["date_note"] = "data = prima incheiere de contract publicata in TED" if cds else ""
    g["fw"] = any(b["fw"] for b in lst)
    g["folder"] = next((b["folder"] for b in lst if b["folder"]), None)
    g["has_key"] = any(b["folder"] or b["prior"] or b["fmt"] in ("legacy_cn", "ted_fara_xml") for b in lst)
    # valoare atribuita: eForms CAN TotalAmount > F03 VAL_TOTAL > DB
    aw = [b for b in lst if b["awarded"] and b["is_award_notice"]] or [b for b in lst if b["awarded"]]
    _ted_aw = [b for b in aw if str(b.get("awarded_src", "")).startswith("TED")]
    aw = _ted_aw or aw
    aw.sort(key=lambda b: (-(b["awarded"] or 0), b["fmt"] != "eforms", b["fmt"] != "legacy_can", b["nid"]))
    g["awarded"] = aw[0]["awarded"] if aw else None; g["awarded_src"] = aw[0].get("awarded_src", "") if aw else ""; g["awarded_note"] = (aw[0].get("awarded_note") or "") if aw else ""
    if len(aw) > 1 and (aw[0]["awarded"] or 0) > 50 * min(b["awarded"] for b in aw): g["awarded_spread"] = f"valorile totale atribuite publicate pentru aceeasi procedura difera de peste 50 de ori intre anunturi ({round(min(b['awarded'] for b in aw))} - {round(aw[0]['awarded'])} RON); posibil eroare de publicare - verificati anunturile"
    if len(aw) > 1: g["awarded_note"] = (g["awarded_note"] + "; " if g["awarded_note"] else "") + f"cea mai mare valoare totala publicata dintre {len(aw)} anunturi de atribuire (din anuntul {aw[0]['nid']}; valorile pe anunturi pot fi partiale sau cumulative)"
    elif aw and aw[0]["nid"] != head["nid"]: g["awarded_note"] = (g["awarded_note"] + "; " if g["awarded_note"] else "") + f"valoare atribuita din anuntul {aw[0]['nid']}"
    # valoare maxima: BT-118 > suma loturi > estimat eForms > F02/F03 estimat > OT
    _order = ["TED eForms BT-118", "TED eForms (suma", "TED eForms (valoare estimata", "TED F02", "TED F03", "SICAP/OpenTender"]
    pri = {}
    def _pri(src): return next((i for i, pfx in enumerate(_order) if src.startswith(pfx)), 9)
    fm = sorted([b for b in lst if b["fw_max"]], key=lambda b: _pri(b["fw_max_src"]))
    if fm:
        best = _pri(fm[0]["fw_max_src"]); cls = [b for b in fm if _pri(b["fw_max_src"]) == best]
        top = max(cls, key=lambda b: b["fw_max"]); g["fw_max"], g["fw_max_src"] = top["fw_max"], top["fw_max_src"]
    else: g["fw_max"], g["fw_max_src"] = None, ""
    fe = [b["fw_max_est"] for b in lst if b.get("fw_max_est")]; g["fw_max_est"] = max(fe) if fe else None
    g["all_vals"] = {round(v) for b in lst for v in (b.get("awarded"), b.get("fw_max")) if v}
    g["member_notes"] = [b[k2] for b in lst for k2 in ("ot_value_ignored", "date_note_sicap") if b.get(k2)]
    g["ted_any"] = any(is_ted_id(b["nid"]) for b in lst)
    # durata: eForms CAN > eForms CN > F02 > OT
    dpri = {"TED eForms (durata publicata)": 0, "TED eForms (data incheierii publicata)": 1, "TED F02 (durata publicata)": 2, "TED F02 (data incheierii publicata)": 3, "SICAP/OpenTender (durata publicata, zile)": 4, "SICAP/OpenTender (data incheierii publicata)": 5}
    dd = sorted([b for b in lst if b["dur_src"]], key=lambda b: dpri.get(b["dur_src"], 9))
    a0 = dparse(g["award"])
    if dd and dd[0]["dur"]: g["dur"] = dd[0]["dur"]; g["dur_src"] = dd[0]["dur_src"]; g["exp"] = add_months(a0, g["dur"])
    elif dd and dd[0]["end_pub"] and dparse(dd[0]["end_pub"]): g["dur"] = None; g["dur_src"] = dd[0]["dur_src"]; g["exp"] = dparse(dd[0]["end_pub"])
    else: g["dur"] = 24; g["dur_src"] = "ESTIMAT (24 luni, durata nepublicata)"; g["exp"] = add_months(a0, 24)
    g["title"] = next((b["title"] for b in lst if b["title"]), "")
    g["vt"] = head["vt"]; g["srcs"] = set().union(*[b["srcs"] for b in lst])
    g["alte"] = [b["nid"] for b in lst if b["nid"] != head["nid"]]
    g["value"], g["basis"] = None, ""
    return g
procs = collections.OrderedDict()
for k, lst in list(groups.items()):
    g = build_proc(lst)
    if not g["winners"]:   # grup format doar din anunturi de participare / randuri fara castigator
        for b in lst:
            for r in b["raw"]: add_trace(r, b["nid"], "", "exclus: procedura fara anunt de atribuire cu castigator")
        excl_raw.append((g["nid"], g["hospital"], "", g.get("fw_max"), g["award"], "procedura fara anunt de atribuire cu castigator (doar anunt de participare / castigator neidentificat)")); continue
    procs[g["nid"]] = g
    for b in lst:
        for r in b["raw"]: add_trace(r, b["nid"], g["nid"], "acelasi anunt" if b["nid"] == g["nid"] else (b.get("join") or "acelasi grup"))
print("proceduri consolidate:", len(procs))

# ---------- 6. inregistrari SICAP (fara identificator TED, ne-negociate) ale unei proceduri TED deja in set ----------
subs = []
by_hc = collections.defaultdict(list)
for g in procs.values(): by_hc[(hnorm(g["hospital"]), str(g["cpv"])[:5])].append(g)
def vals(g): return {round(v) for v in (g.get("awarded"), g.get("fw_max"), g.get("value")) if v} | set(g.get("all_vals") or set())
def is_mirror(head, g):
    """g = grup format doar din inregistrari SICAP; head = procedura TED. Aceeasi procedura daca: castigatori comuni,
    titlu compatibil, valoare in +/-10% fata de o valoare cunoscuta a procedurii (daca ambele au valori) si data
    inregistrarii SICAP intre data atribuirii si expirarea procedurii TED."""
    if g.get("has_key") or not head.get("has_key"): return False
    if any(b.get("negociat") for b in g["members"]): return False
    if not ({wnorm(x) for x in head["winners"]} & {wnorm(x) for x in g["winners"]}): return False
    if title_sim(head.get("title"), g.get("title")) < 0.3: return False
    hv, gv = vals(head), vals(g)
    if hv and gv and not any(abs(x - y) / max(x, y) <= 0.10 for x in hv for y in gv): return False
    ga, ha = dparse(g["award"]), dparse(head["award"])
    return ga and ha and (ha - datetime.timedelta(days=30)) <= ga <= head["exp"]
for k, lst in by_hc.items():
    heads = [g for g in lst if g.get("has_key")]
    for g in lst:
        if g.get("has_key"): continue
        h = next((h for h in heads if is_mirror(h, g)), None)
        if h is None: continue
        g["sub_of"] = h["nid"]; subs.append(g)
        h["alte"] = h.get("alte", []) + [g["nid"]] + [b["nid"] for b in g["members"] if b["nid"] != g["nid"]]
        if g.get("awarded") and not h.get("awarded"): h["awarded"] = g["awarded"]; h["awarded_src"] = g.get("awarded_src", "")
        for x in g["winners"]:
            if wnorm(x) not in {wnorm(y) for y in h["winners"]}: h["winners"].append(x)
for g in subs:
    procs.pop(g["nid"], None)
    for b in g["members"]:
        for r in b["raw"]:
            for i2, t in enumerate(trace):
                if t[0] == r: trace[i2] = (t[0], t[1], g["sub_of"], f"inregistrare SICAP a procedurii {g['sub_of']} (castigatori, valoare, titlu, perioada)")
print("inregistrari SICAP atasate:", len(subs), "-> proceduri finale:", len(procs))
# valoarea finala (dupa atasari)
for g in procs.values():
    g["value"], g["basis"] = (g["fw_max"], "valoare maxima a acordului-cadru (" + g["fw_max_src"] + ")") if g["fw"] and g["fw_max"] else \
        ((g["awarded"], "valoare atribuita (" + (g.get("awarded_src") or "anunt de atribuire") + ")") if g["awarded"] else ((g["fw_max"], "valoare maxima estimata a procedurii (" + g["fw_max_src"] + ")") if g["fw_max"] else (None, "valoare nepublicata")))
for g in procs.values():
    t = strip_diac(g.get("title") or "").upper()
    if re.search(r"NEPERICUL", t): g["scop"] = "titlul indica deseuri NEPERICULOASE (CPV 90524x publicat de autoritate)"
    elif re.search(r"CHIMIC", t) and not re.search(r"MEDICAL|SPITALIC|PERICUL", t): g["scop"] = "titlul indica deseuri CHIMICE (CPV 90524x publicat de autoritate)"
# avertisment pentru duratele estimate: contract negociat/simplificat urmat de un alt contract al aceluiasi spital cu acelasi castigator
byhw = collections.defaultdict(list)
for g in procs.values(): byhw[(hnorm(g["hospital"]), "|".join(sorted(wnorm(x) for x in g["winners"])))].append(g)
for lst in byhw.values():
    lst.sort(key=lambda g: g["award"])
    for i2, g in enumerate(lst):
        est = g["dur_src"].startswith("ESTIMAT")
        lim = add_months(dparse(g["award"]), 18) if est else g["exp"]
        nxt = next((h for h in lst[i2 + 1:] if dparse(h["award"]) > dparse(g["award"]) and dparse(h["award"]) <= lim and (h.get("scop") or "") == (g.get("scop") or "")), None)
        if nxt: g["avert"] = (f"durata estimata; " if est else "") + f"acelasi spital a atribuit un contract nou aceluiasi castigator la {nxt['award']} ({nxt['nid']}), inainte de expirarea calculata => probabil inlocuit"


# avertismente pentru valori/durate publicate implauzibile: valoarea ramane cea din anunt, dar randul este marcat
def _addav(g, msg): g["avert"] = ((g.get("avert") + "; ") if g.get("avert") else "") + msg
for g in procs.values():
    v, aw_, fm_, fe_ = g.get("value") or 0, g.get("awarded") or 0, g.get("fw_max") or 0, g.get("fw_max_est") or 0
    if v > 1e9: _addav(g, "valoare publicata neobisnuit de mare (peste 1 miliard RON); este valoarea din anunt, posibil eroare de publicare a autoritatii - verificati anuntul")
    if g["fw"] and fm_ and aw_ and fm_ > 50 * aw_ and fm_ > 1e7: _addav(g, "valoarea maxima publicata a acordului este de peste 50 de ori valoarea atribuita publicata; posibil eroare de publicare - verificati anuntul")
    if fm_ and fe_ and fm_ > 3 * fe_: _addav(g, "valoarea maxima a acordului (BT-118) depaseste de peste 3 ori valoarea estimata (BT-271) din acelasi anunt; posibil eroare de publicare")
    if aw_ and fm_ and aw_ > 2 * fm_: _addav(g, "valoarea atribuita publicata depaseste de peste 2 ori valoarea maxima/estimata publicata; posibil eroare de publicare")
    if g.get("awarded_spread"): _addav(g, g["awarded_spread"])
    if g.get("dur") and g["dur"] > 60: _addav(g, f"durata publicata neobisnuita ({g['dur']:g} luni); este cea din anunt")
    _late = [d for d in g.get("contract_dates", []) if dparse(d) and dparse(d) > g["exp"]]
    if _late: _addav(g, f"contract publicat dupa data expirarii calculate ({_late[-1]}); durata este probabil subestimata")
    t_ = strip_diac(g.get("title") or "").upper()
    if re.search(r"MEDICAMENT|CITOSTATIC|PERFUZABIL|VACCIN", t_) and not re.search(r"DISPOZITIV|CONSUMABIL|MATERIAL|ECHIPAMENT|APARAT", t_):
        g["scop"] = (g.get("scop") + "; " if g.get("scop") else "") + "titlul indica medicamente (CPV 33x publicat de autoritate)"
# ---------- 7. iesire ----------
def in_win(g): return "DA" if TODAY <= g["exp"] <= H12 else ""
def note(g):
    n = []
    if g.get("scop"): n.append(g["scop"])
    n += g.get("member_notes", [])
    if g.get("hosp_note"): n.append(g["hosp_note"])
    if g.get("date_note"): n.append(g["date_note"])
    if g.get("date_note_bad"): n.append(g["date_note_bad"])
    if g.get("awarded_note"): n.append(g["awarded_note"])
    if g.get("alte"): n.append("aceeasi procedura publicata si sub: " + ", ".join(g["alte"]))
    if g.get("awarded") and g.get("fw_max") and g["awarded"] > g["fw_max"] * 1.001: n.append("valoarea atribuita publicata depaseste valoarea maxima publicata (asa apar in anunturi)")
    return "; ".join(n)
cols = ["id_procedura", "publicat_in_TED", "autoritate_contractanta", "castigatori", "valoare_ron", "baza_valorii", "valoare_atribuita_ron", "sursa_valoare_atribuita", "valoare_max_acord_ron", "sursa_valoare_max", "valoare_max_estimata_acord_ron", "acord_cadru", "titlu", "cpv", "data_atribuirii", "durata_luni", "data_expirarii", "sursa_durata", "expira_in_12_luni", "avertisment", "note", "link"]
def rowof(g):
    return [g["nid"], "DA" if g.get("ted_any") else "NU", g["hospital"], " / ".join(g["winners"]), round(g["value"]) if g.get("value") else "", g["basis"],
            round(g["awarded"]) if g.get("awarded") else "", g.get("awarded_src", ""), round(g["fw_max"]) if g.get("fw_max") else "", g.get("fw_max_src", ""), round(g["fw_max_est"]) if g.get("fw_max_est") else "", "DA" if g["fw"] else "", (g.get("title") or "")[:140], g["cpv"], g["award"],
            g["dur"] if g["dur"] is not None else "", g["exp"].isoformat(), g["dur_src"], in_win(g), g.get("avert", ""), note(g),
            f"https://ted.europa.eu/en/notice/-/detail/{g['nid']}" if is_ted_id(g["nid"]) else f"SICAP anunt nr. {g['nid']}"]
allrows = sorted(procs.values(), key=lambda g: (g["award"], g["nid"]))
with open(f"{OUT}/deseuri_toate_2018_2026.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols); [w.writerow(rowof(g)) for g in allrows]
win = [g for g in allrows if in_win(g)]
with open(f"{OUT}/deseuri_expira_12_luni.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols); [w.writerow(rowof(g)) for g in sorted(win, key=lambda g: g["exp"])]
with open(f"{OUT}/excluse.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id_anunt", "autoritate", "castigator", "valoare_ron", "data", "motiv_excludere"])
    for x in excl_raw: w.writerow([x[0], x[1], x[2], round(x[3]) if x[3] else "", x[4], x[5]])
with open(f"{OUT}/grupare.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id_brut_db", "id_anunt_normalizat", "id_procedura_finala", "relatie"]); [w.writerow(t) for t in trace]
with open(f"{OUT}/ferestre_12_luni.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["fereastra", "contracte_care_expira", "din_care_durata_publicata", "valoare_ron", "contracte_atribuite_in_fereastra", "publicate_in_TED_expira", "publicate_in_TED_valoare_ron", "publicate_in_TED_atribuite"])
    for y in range(2021, TODAY.year + 1):
        a, b = datetime.date(y, TODAY.month, TODAY.day), datetime.date(y + 1, TODAY.month, TODAY.day)
        ws = [g for g in allrows if a <= g["exp"] < b or (b == H12 and g["exp"] == b)]; aw = [g for g in allrows if a <= dparse(g["award"]) < b]
        wt = [g for g in ws if is_ted_id(g["nid"])]; at = [g for g in aw if is_ted_id(g["nid"])]
        w.writerow([f"{a}..{b}", len(ws), sum(1 for g in ws if not g["dur_src"].startswith("ESTIMAT")), round(sum(g.get("value") or 0 for g in ws)), len(aw), len(wt), round(sum(g.get("value") or 0 for g in wt)), len(at)])
# ---------- 8. verificari ----------
chk = []
ids = [g["nid"] for g in allrows]; chk.append(("id unic per procedura", len(ids) == len(set(ids))))
fold = [g["folder"] for g in allrows if g.get("folder")]; chk.append(("ContractFolderID unic intre proceduri", len(fold) == len(set(fold))))
raw_all = [r[0] for r in rows]; tr_ids = [t[0] for t in trace]
chk.append(("fiecare rand brut apare exact o data in grupare.csv", sorted(raw_all) == sorted(tr_ids)))
fin_ids = set(ids) | {""}; chk.append(("fiecare id final din grupare.csv exista in deseuri_toate", all(t[2] in fin_ids for t in trace)))
chk.append((f"toate CPV {_A.cpv_check}*", all(str(g["cpv"]).startswith(_A.cpv_check) for g in allrows)))
chk.append(("nicio autoritate non-spital", all(classify(g["hospital"])[0] == "spital" for g in allrows)))
chk.append(("niciun rand fara castigator", all(g["winners"] for g in allrows)))
chk.append(("niciun titlu 'menajere'", not any(re.search(r"MENAJER", strip_diac(g.get("title") or "").upper()) and not re.search(r"MEDICAL|PERICUL|SPITAL", strip_diac(g.get("title") or "").upper()) for g in allrows)))
chk.append(("fiecare rand are sursa duratei si baza valorii", all(g["dur_src"] and g["basis"] for g in allrows)))
chk.append(("nicio inregistrare SICAP negociata atasata altei proceduri", all(not any(b.get("negociat") for b in g["members"]) or len(g["members"]) == 1 or all(b.get("join", "").startswith(("acelasi anunt", "inregistrare SICAP duplicata")) for b in g["members"]) for g in allrows)))
chk.append(("acord-cadru => valoarea folosita este valoarea maxima a acordului (cand e publicata)", all((not g["fw"]) or (not g.get("fw_max")) or g["basis"].startswith("valoare maxima a acordului") for g in allrows)))
chk.append(("publicat_in_TED = are cel putin un anunt TED", all(("DA" if g.get("ted_any") else "NU") == ("DA" if any(is_ted_id(b["nid"]) for b in g["members"]) else "NU") for g in allrows)))
chk.append(("nicio pereche (spital, castigatori, data, titlu, valoare) duplicata", len({(hnorm(g["hospital"]), "|".join(sorted(wnorm(x) for x in g["winners"])), g["award"], tnorm(g.get("title")), round(g.get("value") or 0)) for g in allrows}) == len(allrows)))
chk.append(("niciun acord-cadru publicat de doua ori (spital, castigatori, titlu, valoare maxima)", len({(hnorm(g["hospital"]), "|".join(sorted(wnorm(x) for x in g["winners"])), tnorm(g.get("title")), round(g.get("fw_max") or 0)) for g in allrows if g["fw"] and g.get("fw_max") and g.get("ted_any")}) == sum(1 for g in allrows if g["fw"] and g.get("fw_max") and g.get("ted_any"))))
_same_day = len(allrows) - len({(hnorm(g["hospital"]), "|".join(sorted(wnorm(x) for x in g["winners"])), g["award"], tnorm(g.get("title"))) for g in allrows})
da_pub = sum(1 for g in win if not g["dur_src"].startswith("ESTIMAT")); da_est = sum(1 for g in win if g["dur_src"].startswith("ESTIMAT")); da_est_av = sum(1 for g in win if g["dur_src"].startswith("ESTIMAT") and g.get("avert")); posib = 0
with open(f"{OUT}/verificari.txt", "w", encoding="utf-8") as f:
    for n, ok in chk: f.write(f"{'OK ' if ok else 'FAIL'} {n}\n")
    f.write(f"\nranduri brute: {len(rows)} | anunturi: {len(ann)} | excluse: {len(excl_raw)} | proceduri finale: {len(allrows)} | inregistrari SICAP atasate unei proceduri TED: {len(subs)}\n")
    f.write(f"expira {TODAY:%d.%m.%Y}-{H12:%d.%m.%Y}: {len(win)} = cu durata publicata {da_pub} + cu durata estimata {da_est} (din care {da_est_av} probabil deja inlocuite, vezi coloana avertisment) | valoare fereastra: {round(sum(g.get('value') or 0 for g in win)/1e6,1)} mil RON\n")
    f.write(f"sursa durata (toate): {dict(collections.Counter(g['dur_src'].split(' (')[0] for g in allrows))}\n")
    f.write(f"baza valorii (toate): {dict(collections.Counter(g['basis'].split(' (')[0] for g in allrows))}\n")
    f.write(f"acorduri-cadru: {sum(1 for g in allrows if g['fw'])} | publicate in TED: {sum(1 for g in allrows if is_ted_id(g['nid']))} | spitale militare: {sum(1 for g in allrows if g.get('hosp_note'))} | fara valoare: {sum(1 for g in allrows if not g.get('value'))}\n")
    f.write("excluse pe motiv: " + str(collections.Counter(x[5].split(' (')[0] for x in excl_raw)) + "\n")
    f.write(f"contracte SICAP distincte (numar de anunt si valoare diferite) ale aceluiasi spital, castigator, zi si titlu (numarate separat, pastrate): {_same_day}\n")
    f.write(f"randuri cu observatie de scop (titlu nepericuloase/chimice): {sum(1 for g in allrows if g.get('scop'))} | randuri din fereastra cu avertisment: {sum(1 for g in win if g.get('avert'))} | erate F14 grupate: {sum(1 for t in trace if 'erata' in t[3])}\n")
print(open(f"{OUT}/verificari.txt").read())
