import numpy as np
from numba import njit
from typing import Dict, Any

@njit(cache=True)
def _calculate_mi_and_stats(events, contexts, n_u, n_s, N):
    joint = np.zeros((n_u, n_s), dtype=np.float64)
    for i in range(N):
        joint[events[i], contexts[i]] += 1.0
    p_joint = joint / N
    p_u = np.sum(p_joint, axis=1)
    p_s = np.sum(p_joint, axis=0)
    
    mi_raw, var_sum, eps = 0.0, 0.0, 1e-12
    for u in range(n_u):
        if p_u[u] < eps: continue
        for s in range(n_s):
            p = p_joint[u, s]
            if p > eps:
                log_ratio = np.log(p / (p_u[u] * p_s[s] + eps))
                mi_raw += p * log_ratio
                var_sum += p * (log_ratio ** 2)
    
    bias = ((n_u - 1.0) * (n_s - 1.0)) / (2.0 * N * 0.693147)
    mi_corrected = mi_raw + bias
    var_est = max(0.0, (var_sum / N) - (mi_corrected ** 2 / N))
    se = np.sqrt(var_est)
    return mi_corrected, se, mi_corrected - 1.96*se, mi_corrected + 1.96*se

# JIT warmup
_warmup_e = np.array([0,1,2], dtype=np.int64)
_warmup_c = np.array([0,1,0], dtype=np.int64)
_calculate_mi_and_stats(_warmup_e, _warmup_c, 3, 2, 3)

def estimate_alignment(events, contexts, min_events=30, max_events=500):
    N = len(events)
    if N == 0: return {'status':'error','reason':'empty_input'}
    if N > max_events:
        idx = np.linspace(0, N-1, max_events, dtype=np.int64)
        events, contexts, N = events[idx], contexts[idx], max_events
    if N < min_events: return {'status':'unreliable','reason':'insufficient_data','n_events':N}
    
    u_unique, s_unique = np.unique(events), np.unique(contexts)
    if len(u_unique)<2 or len(s_unique)<2: 
        return {'status':'unreliable','reason':'degenerate_distribution'}
    
    u_map = {v:i for i,v in enumerate(u_unique)}
    s_map = {v:i for i,v in enumerate(s_unique)}
    me = np.array([u_map[e] for e in events], dtype=np.int64)
    mc = np.array([s_map[c] for c in contexts], dtype=np.int64)
    
    mi, se, ci_l, ci_u = _calculate_mi_and_stats(me, mc, len(u_unique), len(s_unique), N)
    ci_w = ci_u - ci_l
    rel_ci = ci_w / (abs(mi)+1e-8)
    
    return {
        'status':'success',
        'mi_estimate':float(mi),
        'ci_95':[float(ci_l), float(ci_u)],
        'ci_width':float(ci_w),
        'reliable': bool((ci_w < 0.30) and (rel_ci < 0.50)),
        'n_events':int(N),
        'n_u':int(len(u_unique)),
        'n_s':int(len(s_unique))
    }
