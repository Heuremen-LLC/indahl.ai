import pandas as pd
import json
import os
import re
import glob

try:
    CSV_PATH = glob.glob('*.csv')[0]
except IndexError:
    raise FileNotFoundError("No CSV file found in the directory. Please add the raw data CSV.")

OUTPUT_DIR = 'external_dashboards'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"Loading CSV: {CSV_PATH}")
df = pd.read_csv(CSV_PATH, encoding='utf-8')
df.columns = df.columns.str.strip()

for col in ['Metric', 'Period', 'Market', 'Policy type', 'Issue', 'Task type', 'Task']:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()

def clean_result(x):
    if pd.isna(x): return None
    if isinstance(x, str):
        x = x.replace('%', '').replace(',', '').strip()
        if not x or x.lower() in ['nan', 'none', 'null', 'missing']: return None
    try:
        return float(x)
    except ValueError:
        return None

df['Result'] = df['Result'].apply(clean_result)

df_global = df[df['Market'].str.lower().isin(['global', 'all'])].copy()

def get_sort_key(p):
    if pd.isna(p) or p == 'nan': return "0000"
    mapping = {"Jan-Mar": "Q1", "Apr-Jun": "Q2", "Jul-Sep": "Q3", "Oct-Dec": "Q4", "Jan-Jun": "H1", "Jul-Dec": "H2"}
    for k, v in mapping.items():
        if p.startswith(k):
            year = p.split(" ")[-1]
            return f"{year}{v}"
    return p

all_periods = sorted(df_global['Period'].dropna().unique().tolist(), key=get_sort_key)
all_periods = [p for p in all_periods if p != 'nan']

def trim_timeline(periods, *arrays):
    valid_indices = [i for i, _ in enumerate(periods) if any(pd.notna(arr[i]) for arr in arrays)]
    if not valid_indices: return [], [[] for _ in arrays]
    start, end = valid_indices[0], valid_indices[-1]
    return periods[start:end+1], [arr[start:end+1] for arr in arrays]

def get_metric_array(metric_name, issue_val='All', task_val='All', is_pct=False):
    arr = []
    for p in all_periods:
        mask = (df_global['Period'] == p) & (df_global['Metric'].str.lower() == metric_name.lower())
        
        if issue_val.lower() == 'all':
            mask &= df_global['Issue'].str.lower().isin(['all', 'global', 'none', 'missing', '', 'nan'])
        else:
            mask &= (df_global['Issue'].str.lower() == issue_val.lower())
            
        if task_val.lower() == 'all':
            mask &= df_global['Task'].str.lower().isin(['all', 'global', 'none', 'missing', '', 'nan'])
        else:
            mask &= (df_global['Task'].str.lower() == task_val.lower())
        
        res = df_global[mask]['Result'].dropna()
        if not res.empty:
            val = res.max()
            if is_pct:
                arr.append(float(val) * 100)
            else:
                arr.append(float(val))
        else:
            arr.append(None)
    return arr

v1 = get_metric_array('Video: Removal rate of published', is_pct=True)
l1 = get_metric_array('LIVE: Suspension rate of published', is_pct=True)
c1 = get_metric_array('Comment: Removal rate of published', is_pct=True)
p1_trim, (v1_trim, l1_trim, c1_trim) = trim_timeline(all_periods, v1, l1, c1)

dash1_json = {
    "labels": p1_trim, "videoData": v1_trim, "liveData": l1_trim, "commentData": c1_trim
}

v_tot = get_metric_array('Total videos removed')
v_auto = get_metric_array('Total videos removed', task_val='Automation')
v_res = get_metric_array('Videos restored')
p_v, (v_tot_t, v_auto_t, v_res_t) = trim_timeline(all_periods, v_tot, v_auto, v_res)

a_oth = get_metric_array('Accounts removed', issue_val='Other accounts removed')
a_u13 = get_metric_array('Accounts removed', issue_val='Accounts suspected to be under the age of 13 removed')
a_fak = get_metric_array('Accounts removed', issue_val='Fake accounts removed')
p_a, (a_oth_t, a_u13_t, a_fak_t) = trim_timeline(all_periods, a_oth, a_u13, a_fak)

l_int = get_metric_array('LIVE sessions suspended')
l_res = get_metric_array('LIVE sessions restored')
l_dho = get_metric_array('LIVE creators demonetized or warned')
l_dro = get_metric_array('LIVE sessions demonetized or warned')
p_l, (l_int_t, l_res_t, l_dho_t, l_dro_t) = trim_timeline(all_periods, l_int, l_res, l_dho, l_dro)

c_tot = get_metric_array('Comments removed')
p_c, (c_tot_t,) = trim_timeline(all_periods, c_tot)

dash2_json = {
    "periods_v": p_v, "v_tot": v_tot_t, "v_auto": v_auto_t, "v_res": v_res_t,
    "periods_a": p_a, "a_other": a_oth_t, "a_u13": a_u13_t, "a_fake": a_fak_t,
    "periods_l": p_l, "l_int": l_int_t, "l_res": l_res_t, "l_demo_hosts": l_dho_t, "l_demo_rooms": l_dro_t,
    "periods_c": p_c, "c_tot_b": c_tot_t
}

proactive = get_metric_array('Proactive removal rate', is_pct=True)
lt24 = get_metric_array('Removal rate within 24 hours', is_pct=True)
p_rates, (proactive_t, lt24_t) = trim_timeline(all_periods, proactive, lt24)

VV_ORDER = ["0 views", "1-10 views", "11-100 views", "101-1,000 views", "1,001-10,000 views", "10,001-100,000 views", "100,001-1,000,000 views", ">1,000,000 views"]
TAT_ORDER = ["Less than 2 hours", "Between 2 and 8 hours", "Between 8 and 24 hours", "More than 24 hours"]

def build_histogram(metric_name, master_order):
    m_data = {}
    m_df = df_global[df_global['Metric'].str.lower() == metric_name.lower()]
    for p in all_periods:
        p_data = m_df[m_df['Period'] == p]
        if p_data.empty: continue
        val_map = p_data.groupby('Task')['Result'].max().to_dict()
        total = sum([val_map.get(k, 0) for k in master_order])
        if total > 0:
            mult = 100 if total <= 1.5 else 1  
            m_data[p] = {"labels": master_order, "data": [round(val_map.get(k, 0) * mult, 1) for k in master_order]}
    return [p for p in all_periods if p in m_data], m_data

vv_p, vv_d = build_histogram('Total videos removed', VV_ORDER)
tat_p, tat_d = build_histogram('Percentage of user reports actioned', TAT_ORDER)

dash3_json = {
    "periods": p_rates, "proactive": proactive_t, "lt24": lt24_t,
    "vv_periods": vv_p, "vv_data": vv_d, "tat_periods": tat_p, "tat_data": tat_d
}

dash4_video = {}
dash4_comment = {}
df_video = df_global[df_global['Metric'].str.lower().isin(['category share', 'proactive removal rate', 'removal rate within 24 hours', 'removal rate before any views'])]
df_comment = df_global[df_global['Metric'].str.lower() == 'comments removed']
dash4_periods = [p for p in all_periods if get_sort_key(p) >= '2025Q4']

for p in dash4_periods:
    df_p = df_video[(df_video['Period'] == p) & (df_video['Issue'].str.lower() != 'all')]
    if not df_p.empty:
        headings = {}
        rules = {}
        metrics = {}
        df_share = df_p[df_p['Metric'].str.lower() == 'category share']
        for _, row in df_share.iterrows():
            issue = row['Issue']
            val = float(row['Result']) if pd.notna(row['Result']) else 0
            if str(row['Policy type']).lower() == 'policy': headings[issue] = val
            elif str(row['Policy type']).lower() == 'sub-policy': rules[issue] = val
                
        for issue in set(headings.keys()).union(rules.keys()):
            df_issue = df_p[df_p['Issue'] == issue]
            def get_rate(m_name):
                res = df_issue[df_issue['Metric'].str.lower() == m_name.lower()]['Result']
                if not res.empty and pd.notna(res.max()): return float(res.max())
                return 0
            metrics[issue] = {
                "proactive": get_rate('proactive removal rate'), "under_24h": get_rate('removal rate within 24 hours'), "zero_vv": get_rate('removal rate before any views')
            }
        if headings or rules: dash4_video[p] = {"headings": headings, "rules": rules, "metrics": metrics}

    df_c = df_comment[(df_comment['Period'] == p) & (df_comment['Issue'].str.lower() != 'all')]
    if not df_c.empty:
        headings = {}
        rules = {}
        for _, row in df_c.iterrows():
            issue = row['Issue']
            val = float(row['Result']) if pd.notna(row['Result']) else 0
            if str(row['Policy type']).lower() == 'policy': headings[issue] = val
            elif str(row['Policy type']).lower() == 'sub-policy': rules[issue] = val
        if headings or rules: dash4_comment[p] = {"headings": headings, "rules": rules}

dash4_json = {
    "video_periods": [p for p in dash4_periods if p in dash4_video],
    "comment_periods": [p for p in dash4_periods if p in dash4_comment],
    "video": dash4_video, "comment": dash4_comment
}

df_not_lang = df[df['Metric'].str.lower() != 'percentage of moderators assigned']
raw_markets = [m for m in df_not_lang['Market'].dropna().unique() if str(m).strip().lower() not in ['nan', 'none', '']]
valid_markets = []
for m in sorted(raw_markets):
    if m.lower() in ['all', 'global']: continue
    valid_markets.append(m)
markets = ['All'] + valid_markets if any(m.lower() in ['all', 'global'] for m in raw_markets) else valid_markets

market_data = {}
for m in markets:
    market_data[m] = {}
    m_mask = (df['Market'].str.lower() == m.lower()) | (df['Market'].str.lower() == 'global' if m == 'All' else False)
    df_m = df[m_mask]
    for p in all_periods:
        df_p = df_m[df_m['Period'] == p]
        if df_p.empty: continue
        
        def get_m_val(metric, is_pct=False):
            res = df_p[(df_p['Metric'].str.lower() == metric.lower()) & 
                       (df_p['Issue'].fillna('All').str.lower().isin(['all', 'global', 'none', 'missing', '', 'nan'])) &
                       (df_p['Task'].fillna('All').str.lower().isin(['all', 'global', 'none', 'missing', '', 'nan']))]['Result']
            if not res.empty:
                v = res.max()
                if is_pct: return f"{float(v)*100:.1f}%"
                return float(v)
            return None
        
        rem_count = get_m_val('Total videos removed')
        rem_pub = get_m_val('Video: Removal rate of published', is_pct=True)
        proactive = get_m_val('Proactive removal rate', is_pct=True)
        lt24 = get_m_val('Removal rate within 24 hours', is_pct=True)
        restored = get_m_val('Videos restored')
        
        if any(v is not None for v in [rem_count, rem_pub, proactive, lt24, restored]):
            market_data[m][p] = {
                "rem_count": rem_count, "rem_pub": rem_pub if rem_pub is not None else "N/A",
                "proactive": proactive if proactive is not None else "N/A", "lt24": lt24 if lt24 is not None else "N/A",
                "restored": restored
            }

df_lang = df[df['Metric'].str.lower() == 'percentage of moderators assigned']
lang_data = {}
for p in all_periods:
    df_p = df_lang[df_lang['Period'] == p]
    if not df_p.empty:
        df_p = df_p.sort_values('Result', ascending=False)
        lang_data[p] = {"labels": df_p['Market'].tolist(), "data": [round(float(v)*100, 1) for v in df_p['Result']]}

dash5_json = {"periods": all_periods, "markets": markets, "market_data": market_data, "lang_data": lang_data}

spam_metrics = ['Fake accounts prevented', 'Videos removed from fake accounts', 'Comments removed from fake accounts', 'Fake followers removed', 'Fake likes removed', 'Fake follow requests prevented', 'Fake likes prevented']
dash6_data = {}
for m in spam_metrics:
    raw_arr = get_metric_array(m)
    p_trim, (v_trim,) = trim_timeline(all_periods, raw_arr)
    if p_trim: dash6_data[m] = {"labels": p_trim, "data": v_trim}
        
dash6_colors = {"Fake accounts prevented": "#2dccd3", "Videos removed from fake accounts": "#d946a8", "Comments removed from fake accounts": "#ff9800", "Fake followers removed": "#20d5d2", "Fake likes removed": "#e641a1", "Fake follow requests prevented": "#ff9f21", "Fake likes prevented": "#1ab8b5"}
dash6_json = {"data": dash6_data, "colors": dash6_colors}

ad_rem = get_metric_array('Individual Ads removed')
ad_acc = get_metric_array('Ads removed due to account actions')
p_ads, (ad_rem_t, ad_acc_t) = trim_timeline(all_periods, ad_rem, ad_acc)

dash7_json = {"periods": p_ads, "data": {"Individual Ads removed": ad_rem_t, "Ads removed due to account actions": ad_acc_t}}

def process_template(template_name, dash_json, format_y_axis_volume=False, patch_x_axis=True):
    template_path = os.path.join('templates', template_name)
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        print(f"Skipping {template_name} (File not found)")
        return

    data_injection_str = f"window.injectedData = {json.dumps(dash_json)};"
    html = re.sub(r'/\*\s*INJECT_DATA\s*\*/', lambda _: data_injection_str, html)

    clean_js_block = """
    window.IS_RTL = false;
    window.t = function(key) { return key; };
    """
    html = re.sub(r'/\*\s*INJECT_TRANSLATIONS\s*\*/', lambda _: clean_js_block, html)

    if patch_x_axis:
        old_axis_pattern = r"callback:\s*function\((?:val,\s*i|value,\s*index)\)\s*\{.*?return\s*'';[^\}]*\}"
        new_axis_logic = """callback: function(val, i) { 
            const l = this.getLabelForValue(val);
            if (!l) return '';
            const year = l.slice(-4);
            if (i === 0 || l.startsWith('Jan-') || l.startsWith('H1')) return year;
            return '';
        }"""
        html = re.sub(old_axis_pattern, new_axis_logic, html, flags=re.DOTALL)

    if format_y_axis_volume:
        y_axis_patch = """beginAtZero: true, 
                    ticks: { 
                        callback: function(value) { 
                            if (value >= 1e9) return (value / 1e9) + 'B'; 
                            if (value >= 1e6) return (value / 1e6) + 'M'; 
                            if (value >= 1e3) return (value / 1e3) + 'K'; 
                            return value; 
                        } 
                    }"""
        html = html.replace('beginAtZero: true', y_axis_patch)

    if '4_Policies' in template_name:
        clean_sunburst_logic = """function buildSunburstData(dataObj, isVideo) {
            let ids = ["root_total"], labels = ['Policies'], parents = [""], values = [0], customdata = ["100%"], colors = ["#ffffff"];
            let childrenSum = {};
            Object.keys(dataObj.rules || {}).forEach(rk => {
                let p = rk.split(' - ')[0];
                childrenSum[p] = (childrenSum[p] || 0) + dataObj.rules[rk];
            });

            let totalActualSum = Object.values(dataObj.headings || {}).reduce((a, b) => a + b, 0);
            let rootPlotSum = 0;
            let sortedH = Object.keys(dataObj.headings || {}).sort((a,b) => dataObj.headings[b] - dataObj.headings[a]);

            sortedH.forEach(h => {
                let val = dataObj.headings[h];
                let plotVal = val; 
                
                ids.push(h); labels.push(window.t(h)); parents.push("root_total"); values.push(plotVal);
                colors.push(categoryColors[h] || "#cccccc");
                rootPlotSum += plotVal;

                let rawPct = (val / totalActualSum) * 100;
                let pctStr = (rawPct > 0 && rawPct < 0.1) ? "<0.1%" : rawPct.toFixed(1) + "%";
                let tip = isVideo ? `Share of total removals: ${pctStr}` : `Comments removed: ${val.toLocaleString()}<br>Share of total removals: ${pctStr}`;
                if (isVideo && dataObj.metrics && dataObj.metrics[h]) {
                    tip += `<br>Proactive removal rate: ${(dataObj.metrics[h].proactive * 100).toFixed(1)}%`;
                    tip += `<br>Removal rate within 24 hours: ${(dataObj.metrics[h].under_24h * 100).toFixed(1)}%`;
                    tip += `<br>Video removal 0vv %: ${(dataObj.metrics[h].zero_vv * 100).toFixed(1)}%`;
                }
                customdata.push(tip);

                let rulesInH = Object.keys(dataObj.rules || {}).filter(rk => rk.startsWith(h + " - ")).sort((a,b) => dataObj.rules[b] - dataObj.rules[a]);
                rulesInH.forEach(rk => {
                    let sub = rk.split(' - ').slice(1).join(' - ');
                    let ruleVal = dataObj.rules[rk];
                    let scale = (childrenSum[h] > 0) ? (plotVal / childrenSum[h]) : 1;
                    let finalVal = ruleVal * scale;
                    
                    ids.push(rk); labels.push(window.t(sub)); parents.push(h); values.push(finalVal);
                    colors.push(categoryColors[h] || "#cccccc");

                    let ruleRawPct = (ruleVal / totalActualSum) * 100; 
                    if (isVideo) {
                        ruleRawPct = (finalVal / totalActualSum) * 100;
                    }
                    let rulePctStr = (ruleRawPct > 0 && ruleRawPct < 0.1) ? "<0.1%" : ruleRawPct.toFixed(1) + "%";
                    
                    let ruleTip = isVideo ? `Share of total removals: ${rulePctStr}` : `Comments removed: ${ruleVal.toLocaleString()}<br>Share of total removals: ${rulePctStr}`;
                    if (isVideo && dataObj.metrics && dataObj.metrics[rk]) {
                        ruleTip += `<br>Proactive removal rate: ${(dataObj.metrics[rk].proactive * 100).toFixed(1)}%`;
                        ruleTip += `<br>Removal rate within 24 hours: ${(dataObj.metrics[rk].under_24h * 100).toFixed(1)}%`;
                        ruleTip += `<br>Video removal 0vv %: ${(dataObj.metrics[rk].zero_vv * 100).toFixed(1)}%`;
                    }
                    customdata.push(ruleTip);
                });
            });

            values[0] = rootPlotSum;
            return { ids, labels, parents, values, customdata, colors };
        }"""
        pattern = r'function buildSunburstData\(dataObj, isVideo\) \{.*?\n        \}'
        html = re.sub(pattern, lambda _: clean_sunburst_logic, html, flags=re.DOTALL)

    if '5_Geography' in template_name:
        html = html.replace("includes('all')", "includes('All')")
        html = html.replace("currentMarket = 'all'", "currentMarket = 'All'")
    if '7_Ads' in template_name:
        html = html.replace("labels.indexOf('2025Q4')", "labels.findIndex(l => l.includes('Oct-Dec 2025') || l === '2025Q4')")

    html = re.sub(r'<div class="(info-box|footnote-box)".*?</div>', '', html, flags=re.DOTALL)
    html = re.sub(r'\{\{(.*?)\}\}', r'\1', html)

    output_path = os.path.join(OUTPUT_DIR, template_name.replace('_Template', ''))
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ Success! Created {output_path}")

print("\nProcessing HTML files...")
process_template('1_Prevalence_Template.html', dash1_json)
process_template('2_Volume_Template.html', dash2_json, format_y_axis_volume=True)
process_template('3_Speed_Template.html', dash3_json)
process_template('4_Policies_Template.html', dash4_json, patch_x_axis=False)
process_template('5_Geography_Template.html', dash5_json, patch_x_axis=False)
process_template('6_Spam_Template.html', dash6_json, format_y_axis_volume=True)
process_template('7_Ads_Template.html', dash7_json, format_y_axis_volume=True)