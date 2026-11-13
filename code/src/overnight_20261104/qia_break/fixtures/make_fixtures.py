"""Generate every qia-check break fixture as IBM BackendProperties-shaped JSON (DRAFT, Sage, 2026-11-03).
Shape follows json.dump(backend.properties().to_dict(), f, default=str): qubits = list of lists of Nduv
{date, name, unit, value}; gates = list of {gate, qubits, parameters[Nduv], name}. Dates default to the
str(datetime) form that default=str produces ('2026-11-01 12:00:00+00:00').
Run: python make_fixtures.py   (wipes and rewrites ./data/ so nothing is left over)."""
import json, os, shutil, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
UTC = dt.timezone.utc
EDT = dt.timezone(dt.timedelta(hours=-4))
EST = dt.timezone(dt.timedelta(hours=-5))
S0 = dt.datetime(2026, 11, 1, 12, 0, 0, tzinfo=UTC)          # base record stamp


def H(h):
    return dt.timedelta(hours=h)


SEC = dt.timedelta(seconds=1)


def ts(d):
    return str(d) if isinstance(d, dt.datetime) else d        # default=str form, or a raw string / None


def nduv(name, value, date, unit=''):
    return {'date': ts(date), 'name': name, 'unit': unit, 'value': value}


def qubit(T1=152.31, T2=118.74, t1d=None, t2d=None, ro=0.0122, p01=0.0151, p10=0.0093, rod=None, p01d=None, p10d=None,
          t1u='us', t2u='us', omit=(), extra=(), stamp=S0, t1_date_null=False):
    """One qubit's Nduv list in IBM order. Default dates: T1 3 h before stamp, T2 2h53m before, readout 2.5 h before."""
    t1d = stamp - H(3) if t1d is None else t1d
    t2d = stamp - H(3) + dt.timedelta(minutes=7) if t2d is None else t2d
    rod = stamp - H(2.5) if rod is None else rod
    p01d = rod if p01d is None else p01d
    p10d = rod if p10d is None else p10d
    L = [nduv('T1', T1, None if t1_date_null else t1d, t1u), nduv('T2', T2, t2d, t2u),
         nduv('frequency', 4.8312, stamp - H(4), 'GHz'), nduv('anharmonicity', -0.3095, stamp - H(4), 'GHz'),
         nduv('readout_error', ro, rod), nduv('prob_meas0_prep1', p01, p01d), nduv('prob_meas1_prep0', p10, p10d),
         nduv('readout_length', 1560.0, stamp - H(4), 'ns')]
    L = [x for x in L if x['name'] not in omit]
    return L + list(extra)


def gates(n, stamp=S0, edge_params=None):
    g = []
    for q in range(n):
        for name in ('id', 'sx', 'x'):
            g.append({'gate': name, 'qubits': [q], 'name': f'{name}{q}',
                      'parameters': [nduv('gate_error', 2.4e-4, stamp - H(5)), nduv('gate_length', 32.0, stamp - H(5), 'ns')]})
    for q in range(n - 1):
        ps = [nduv('gate_error', 0.0042, stamp - H(5)), nduv('gate_length', 68.0, stamp - H(5), 'ns')]
        ps += (edge_params or {}).get((q, q + 1), [])
        g.append({'gate': 'cz', 'qubits': [q, q + 1], 'parameters': ps, 'name': f'cz{q}_{q + 1}'})
    return g


def record(qs, stamp=S0, backend='ibm_kingston', edge_params=None, raw_stamp=None):
    return {'backend_name': backend, 'backend_version': '1.27.3',
            'last_update_date': raw_stamp if raw_stamp is not None else ts(stamp),
            'qubits': qs, 'gates': gates(max(len(qs), 2), stamp, edge_params), 'general': [], 'general_qlists': []}


def put(rel, obj=None, text=None):
    p = os.path.join(DATA, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text if text is not None else json.dumps(obj, indent=1))  # NaN is written as NaN, as json.dump does
    return p


def build():
    if os.path.isdir(DATA):
        shutil.rmtree(DATA)
    # ================= plan fixtures (drafts/qia-check-break-plan.md, items 1-14) =================
    # P01 init_error measured 84 d before the stamp, T1/T2 fresh (Q10, plan wording)
    put('P01/record.json', record([qubit(extra=[nduv('init_error', 0.0031, S0 - dt.timedelta(days=84))]), qubit()]))
    # P02 prob_meas0_prep1 97 h older than readout_error (Q11)
    put('P02/record.json', record([qubit(p01d=S0 - H(2.5) - H(97)), qubit()]))
    # P03 record stamped 72 h before the run, T1/T2 measured 1 h before the stamp
    r3 = record([qubit(t1d=S0 - H(1), t2d=S0 - H(1)) for _ in range(2)])
    put('P03/record.json', r3)
    put('P03/records/rec_s0.json', r3)
    # P04 q0 T1 absent, q1 T1 null, q2 T1 NaN, q3 T1 date null, q4 T1 = 0, q5 T2 NaN, q6 T2 absent, q7 control (T2/T1 2.63)
    put('P04/record.json', record([qubit(omit=('T1',)), qubit(T1=None), qubit(T1=float('nan')), qubit(t1_date_null=True),
                                   qubit(T1=0.0), qubit(T2=float('nan')), qubit(omit=('T2',)), qubit(T2=400.0)]))
    # P05 zz = 0.00 on edge 0-1 whose CZ gate_error is calibrated; edge 1-2 has zz 12.4 kHz
    put('P05/record.json', record([qubit(), qubit(), qubit()],
                                  edge_params={(0, 1): [nduv('zz', 0.0, S0 - H(5), 'kHz')], (1, 2): [nduv('zz', 12.4, S0 - H(5), 'kHz')]}))
    # P06 T1 age exactly 24h00m00s (q0), 23h59m59s (q1), 24h00m01s (q2 control)
    put('P06/record.json', record([qubit(t1d=S0 - H(24)), qubit(t1d=S0 - H(24) + SEC), qubit(t1d=S0 - H(24) - SEC)]))
    # P07 one instant (stamp - 22 h = 2026-10-31 14:00 UTC = 10:00 EDT) in six spellings; stamp written with Z
    inst = S0 - H(22)
    spell = {'a_edt_offset': inst.astimezone(EDT).isoformat(),
             'b_utc_Z': inst.strftime('%Y-%m-%dT%H:%M:%SZ'),
             'c_plus0000': inst.isoformat(),
             'd_naive_utc_wall': inst.strftime('%Y-%m-%dT%H:%M:%S'),
             'e_naive_edt_wall': inst.astimezone(EDT).strftime('%Y-%m-%dT%H:%M:%S'),
             'f_edt_abbrev': inst.astimezone(EDT).strftime('%Y-%m-%dT%H:%M:%S') + ' EDT'}
    for k, s in spell.items():
        put(f'P07/{k}.json', record([qubit(t1d=s, t2d=s)], raw_stamp=S0.strftime('%Y-%m-%dT%H:%M:%SZ')))
    # P08 ZERO: q0 1e-17, q1 -0.0, q2 "0" (string), q3 1/1024, q4 0 (control)
    put('P08/record.json', record([qubit(ro=1e-17), qubit(ro=-0.0), qubit(ro='0'), qubit(ro=0.0009765625), qubit(ro=0)]))
    # P09 T2/T1 = 2.0, 2.0000001, 2.5, 2.5000001; q4, q5 are decimal-exact 2.5 that float division moves off 2.5
    put('P09/record.json', record([qubit(T1=150.0, T2=300.0), qubit(T1=150.0, T2=300.000015), qubit(T1=150.0, T2=375.0),
                                   qubit(T1=150.0, T2=375.000015), qubit(T1=0.0001234, T2=0.0003085, t1u='s', t2u='s'),
                                   qubit(T1=143.21, T2=358.025)]))
    # P10 PAIR: T1/T2 dates exactly 24 h apart (q0), 24h00m01s (q1), 23h59m59s (q2)
    put('P10/record.json', record([qubit(t1d=S0 - H(24), t2d=S0), qubit(t1d=S0 - H(24) - SEC, t2d=S0),
                                   qubit(t1d=S0 - H(24) + SEC, t2d=S0)]))
    # P11 run 12:00-12:40 spans a restamp at 12:20 (q0 T1 152.31 -> 97.4); a 13:00 record lies after the window
    s1, s2, s3 = S0 - H(1), S0 + dt.timedelta(minutes=20), S0 + H(1)
    put('P11/records/a_1100.json', record([qubit(stamp=s1), qubit(stamp=s1)], stamp=s1))
    put('P11/records/b_1220.json', record([qubit(T1=97.4, t1d=s2 - H(0.2), stamp=s1), qubit(stamp=s1)], stamp=s2))
    put('P11/records/c_1300.json', record([qubit(T1=88.0, stamp=s3), qubit(stamp=s3)], stamp=s3))
    # P12 stamp moves S0, S0+12h, S0+36h; every T1/T2/readout value and date frozen at S0-1h (Q6)
    for i, mv in enumerate((0, 12, 36)):
        put(f'P12/records/r{i}_{mv:02d}h.json',
            record([qubit(t1d=S0 - H(1), t2d=S0 - H(1), rod=S0 - H(1)) for _ in range(2)], stamp=S0 + H(mv)))
    # P13 grid: k/1024 readout values written rounded (0.00293 ~ 3/1024) vs exact; q2 is 3/4096
    put('P13/record.json', record([qubit(ro=0.00293, p01=0.00391, p10=0.00195),
                                   qubit(ro=0.0029296875, p01=0.00390625, p10=0.001953125), qubit(ro=0.000732421875)]))
    # P14 YO vs code: the 23h59m59s and 1e-17 inputs
    put('P14/record.json', record([qubit(t1d=S0 - H(24) + SEC), qubit(ro=1e-17)]))
    # ================= extra fixtures (task step 5) =================
    good = json.dumps(record([qubit()]), indent=1)
    put('E01/truncated.json', text=good[: len(good) // 2])
    put('E01/trailing_comma.json', text='{"backend_name": "ibm_kingston", "last_update_date": "2026-11-01 12:00:00+00:00", "qubits": [[]],}')
    put('E01/list_top.json', text='[' + good + ']')
    put('E01/no_stamp.json', obj={k: v for k, v in record([qubit()]).items() if k != 'last_update_date'})
    put('E01/dir/good.json', record([qubit()], stamp=S0 - H(1)))
    put('E01/dir/bad.json', text=good[:200])
    put('E02/empty.json', record([]))
    put('E02/empty_qubit.json', record([[], qubit()]))
    put('E03/stale_first.json', record([[nduv('T1', 152.31, S0 - H(48), 'us')] + qubit()]))   # stale T1, then fresh T1
    put('E03/stale_last.json', record([qubit() + [nduv('T1', 152.31, S0 - H(48), 'us')]]))    # fresh T1, then stale T1
    put('E03/ratio_conflict.json', record([qubit(T1=150.0, T2=400.0) + [nduv('T1', 210.0, S0 - H(3), 'us')]]))
    # E04 negative T1. q0: |T1| would give T2/T1 2.66. q1: T1/T2 dates 30 h apart as well
    put('E04/record.json', record([qubit(T1=-150.2, T2=400.0), qubit(T1=-150.2, T2=400.0, t1d=S0 - H(31), t2d=S0 - H(1))]))
    # E05 units: q0 T1 in s / T2 in us; q1 T1 in us / T2 in s (true ratio 2.66); q2 T1 in ms / T2 in us
    put('E05/record.json', record([qubit(T1=0.0001502, t1u='s', T2=118.74, t2u='us'),
                                   qubit(T1=150.2, t1u='us', T2=0.00040, t2u='s'),
                                   qubit(T1=0.1502, t1u='ms', T2=400.0, t2u='us')]))
    put('E06/numbers_as_strings.json', record([qubit(T1='152.31', T2='118.74')]))
    put('E06/zero_as_string.json', record([qubit(ro='0.0'), qubit(p01='0')]))
    put('E06/err_as_string_nonzero.json', record([qubit(ro='0.0122', T2='400.0', T1=150.0)]))
    put('E07/leap_t1.json', record([qubit(t1d='2016-12-31T23:59:60Z', t2d='2017-01-01T00:00:00Z')], raw_stamp='2017-01-01T06:00:00Z'))
    put('E07/leap_stamp.json', record([qubit(t1d='2016-12-31T12:00:00Z', t2d='2016-12-31T12:00:00Z')], raw_stamp='2016-12-31T23:59:60Z'))
    # US fall-back 2026-11-01 02:00 EDT -> 01:00 EST. T1 01:45 EDT 31 Oct (05:45Z); stamp 01:15 EST 1 Nov (06:15Z):
    # true age 24.5 h (stale), wall-clock difference 23.5 h
    t1 = dt.datetime(2026, 10, 31, 1, 45, tzinfo=EDT)
    st = dt.datetime(2026, 11, 1, 1, 15, tzinfo=EST)
    put('E07/dst_aware.json', record([qubit(t1d=t1.isoformat(), t2d=st.isoformat())], raw_stamp=st.isoformat()))
    put('E07/dst_naive_walls.json', record([qubit(t1d=t1.strftime('%Y-%m-%dT%H:%M:%S'), t2d=st.strftime('%Y-%m-%dT%H:%M:%S'))],
                                           raw_stamp=st.strftime('%Y-%m-%dT%H:%M:%S')))
    # E08 Q10 shape: readout_error, prob_meas0_prep1, prob_meas1_prep0 dated 84 d before the stamp; T1/T2 fresh
    old = S0 - dt.timedelta(days=84)
    put('E08/record.json', record([qubit(rod=old, p01d=old, p10d=old), qubit()]))
    # ================= derived from the source reading =================
    # D01 T1 value null (q0) or negative (q1); T1 date 33 h, T2 date 3 h before stamp, so 30 h apart: PAIR should still fire
    put('D01/record.json', record([qubit(T1=None, t1d=S0 - H(33), t2d=S0 - H(3)), qubit(T1=-1.0, t1d=S0 - H(33), t2d=S0 - H(3)),
                                   qubit(t1d=S0 - H(33), t2d=S0 - H(3))]))   # q2 control: valid T1
    # D02 two backends in one after folder: kingston 11:00, fez 11:50
    put('D02/records/a_kingston_1100.json', record([qubit(stamp=s1) for _ in range(2)], stamp=s1))
    put('D02/records/b_fez_1150.json', record([qubit(T1=61.0, t1d=S0 - H(40)) for _ in range(2)],
                                              stamp=S0 - dt.timedelta(minutes=10), backend='ibm_fez'))
    # D03 record stamped during the run carries a ZERO and a 60 h stale T1 on q1
    put('D03/records/a_1100.json', record([qubit(stamp=s1) for _ in range(2)], stamp=s1))
    put('D03/records/b_1220.json', record([qubit(stamp=s1), qubit(ro=0.0, t1d=S0 - H(60), stamp=s1)], stamp=s2))
    # D04 two files with the same stamp and different contents (b: T1 41 us, 50 h stale)
    put('D04/records/a.json', record([qubit(T1=152.31)]))
    put('D04/records/b.json', record([qubit(T1=41.0, t1d=S0 - H(50))]))
    return DATA


if __name__ == '__main__':
    print('fixtures written to', build())
