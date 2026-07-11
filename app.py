import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# ==========================================
# 1. 页面配置与基础样式（深度优化排版间距）
# ==========================================
st.set_page_config(page_title="心血管-肾脏-代谢综合征(CKM)自动分期决策系统", layout="wide")

st.markdown(
"""
<style>
/* 1. 全局及 Streamlit 原生容器修复 */
.main .block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

[data-testid="stFormRow"], [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
}

/* 2. 📱 移动端专有响应式适配 (屏幕宽度 <= 768px) */
@media screen and (max-width: 768px) {
    /* 1. 专门修复首页标题：允许正常换行、微调字号 */
    .cover-title {
        font-size: 1.55rem !important;  /* 稍微缩小字号，确保正好排成两行 */
        line-height: 1.4 !important;
        word-break: normal !important;  /* 允许中文字符正常换行 */
        white-space: normal !important;
        padding: 0 5px !important;
    }
    
    /* 2. 首页按钮专用的容器适配 */
    .cover-btn-container [data-testid="stColumn"] {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        flex: 0 0 100% !important;
    }

    .block-container {
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
    }

    /* 核心修复：强行重置 Streamlit 的横向 Block 为 Flex 换行模式 */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px 8px !important;
        width: 100% !important;
    }

    /* 主页面的表单 Grid 控制：一排两个 (50% 宽度) */
    .main [data-testid="stColumn"] {
        width: calc(50% - 4px) !important;
        min-width: calc(50% - 4px) !important;
        max-width: calc(50% - 4px) !important;
        flex: 0 0 calc(50% - 4px) !important;
        margin-bottom: 4px !important;
    }

    /* 如果 Column 内只有 checkbox，也保持良好排列 */
    [data-testid="stColumn"] [data-testid="stCheckbox"] {
        padding-top: 4px;
    }

    /* 解决输入框文字太小/截断问题 */
    div[data-baseweb="input"] {
        width: 100% !important;
    }
    
    div[data-baseweb="input"] input {
        font-size: 14px !important;
        padding: 6px 6px !important;
        height: 38px !important;
    }
    
    /* Input 标签文字规范 */
    label p {
        font-size: 12px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin-bottom: 2px !important;
    }

    /* Metric 卡片字号适配 */
    [data-testid="stMetricValue"] {
        font-size: 1.0rem !important;
    }
}

/* 3. 🖨️ 打印媒体查询 */
@media print {
    header, footer, [data-testid="stHeader"], .no-print, button, iframe, [data-testid="element-container"]:has(.no-print) {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    html, body, .stApp, .print-report-container {
        height: auto !important;
        overflow: visible !important;
        font-size: 12px !important;
        background-color: #ffffff !important;
    }
    
    .print-report-container {
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    @page {
        margin: 8mm 12mm 8mm 12mm;
        size: auto;
    }
}
</style>
""", unsafe_allow_html=True
)
# ==========================================
# 2. 状态初始化与辅助函数
# ==========================================
if "page" not in st.session_state: st.session_state.page = "cover"
if "is_locked" not in st.session_state: st.session_state.is_locked = False

def get_val(key, default=None):
    val = st.session_state.get(key)
    return val if val is not None else default

# ==========================================
# 3. 路由控制
# ==========================================

# ------- 路由A：欢迎封面页 -------
if st.session_state.page == "cover":
    # 顶部留白由 15vh 缩减为 10vh，避免手机屏整体太靠下
    st.markdown("<div style='margin-top: 10vh;'></div>", unsafe_allow_html=True)
    
    # 手动用 <br> 严格精准控制 2 行换行
    st.markdown(
        """
        <div style='text-align:center; max-width: 100%; margin: 0 auto; padding: 10px;'>
            <h1 class='cover-title' style='color:#1E3A8A; font-weight: 800; margin-bottom: 40px;'>
                心血管-肾脏-代谢综合征 (CKM)<br>自动分期决策系统
            </h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 增加 class='cover-btn-container'，确保手机端按钮宽度不会被切成 50%
    st.markdown("<div class='cover-btn-container'>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([0.8, 3.4, 0.8])
    with btn_col:
        if st.button("进入系统 ➔", use_container_width=True, type="primary"):
            st.session_state.page = "main"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ------- 路由B：纯净打印预览报告页 -------
elif st.session_state.page == "print_view":
    p_name = get_val("p_name", "未填写")
    p_id = get_val("p_id", "未填写")
    p_age = get_val("p_age", "--")
    p_gender = get_val("p_gender", "--")
    
    labs = {
        "收缩压": (get_val("p_sbp"), "mmHg", "%.0f"),
        "舒张压": (get_val("p_dbp"), "mmHg", "%.0f"),
        "空腹血糖": (get_val("p_fpg"), "mmol/L", "%.2f"),
        "餐后2小时血糖": (get_val("p_2hpg"), "mmol/L", "%.2f"),
        "糖化血红蛋白": (get_val("p_hba1c"), "%", "%.1f"),
        "总胆固醇": (get_val("p_tc"), "mmol/L", "%.2f"),
        "甘油三酯": (get_val("p_tg"), "mmol/L", "%.2f"),
        "低密度脂蛋白": (get_val("p_ldl"), "mmol/L", "%.2f"),
        "高密度脂蛋白": (get_val("p_hdl"), "mmol/L", "%.2f"),
        "B型脑钠肽前体": (get_val("p_bnp"), "pg/mL", "%.0f"),
        "肌酐": (get_val("p_scr"), "μmol/L", "%.1f"),
        "胱抑素C": (get_val("p_cysc"), "mg/L", "%.2f"),
        "尿白蛋白肌酐比": (get_val("p_uacr"), "mg/g", "%.2f"),
        "肌钙蛋白T": (get_val("p_ctnt"), "ng/mL", "%.3f"),
        "肌钙蛋白I": (get_val("p_ctni"), "μg/L", "%.3f"),
    }

    st.markdown('<div class="print-report-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#1E3A8A; margin-top:5px; margin-bottom:15px; font-size:1.5rem;'>心血管-肾脏-代谢综合征(CKM) 临床评估报告单</h3>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <table style='width:100%; border-collapse: collapse; margin-bottom: 12px; font-size:0.95rem;'>
        <tr style='background-color:#F3F4F6;'>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px; font-weight:bold; width:15%;'>患者姓名</td>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px; width:35%;'>{p_name}</td>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px; font-weight:bold; width:15%;'>ID号</td>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px; width:35%;'>{p_id}</td>
        </tr>
        <tr>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px; font-weight:bold;'>年龄</td>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px;'>{p_age} 岁</td>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px; font-weight:bold;'>性别</td>
            <td style='border: 1px solid #D1D5DB; padding: 6px 10px;'>{p_gender}</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)

    st.markdown("<h5 style='margin: 0 0 5px 0; font-size:1.05rem;'>📋 已确诊疾病史及临床危险因素</h5>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:8px; border-top:1px solid #D1D5DB;'>", unsafe_allow_html=True)
    
    history_list = get_val("p_history_tags", [])
    if history_list:
        tags_html = "".join([f"<span style='display:inline-block; background-color:#EFF6FF; color:#1E40AF; border:1px solid #BFDBFE; padding:3px 8px; margin:2px 4px 2px 0; border-radius:4px; font-size:0.85rem; font-weight:500;'>✓ {item}</span>" for item in history_list])
        st.markdown(f"<div style='margin-bottom:12px;'>{tags_html}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#6B7280; font-size:0.85rem; margin-bottom:12px;'>未勾选相关疾病史及危险因素（无既往特殊病史）</p>", unsafe_allow_html=True)
    
    st.markdown("<h5 style='margin: 0 0 5px 0; font-size:1.05rem;'>🧪 生理指标与检验结果</h5>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:8px; border-top:1px solid #D1D5DB;'>", unsafe_allow_html=True)
    
    items = list(labs.items())
    html_grid = "<table style='width:100%; border-collapse: collapse; font-size:0.85rem; text-align:left; margin-bottom:15px;'>"
    for i in range(0, len(items), 5):
        chunk = items[i:i+5]
        html_grid += "<tr>"
        for label, (val, unit, fmt) in chunk:
            html_grid += f"<td style='padding:4px 4px 2px 4px; color:#4B5563; font-weight:500; width:20%;'>{label}</td>"
        html_grid += "</tr><tr>"
        for label, (val, unit, fmt) in chunk:
            display = f"{val:{fmt.replace('%','')}} {unit}" if val is not None else "--"
            html_grid += f"<td style='padding:2px 4px 8px 4px; font-size:0.95rem; font-weight:bold; border-bottom:1.5px solid #E5E7EB; color:#000;'>{display}</td>"
        html_grid += "</tr>"
    html_grid += "</table>"
    st.markdown(html_grid, unsafe_allow_html=True)
    
    st.markdown("<h5 style='margin: 0 0 5px 0; font-size:1.05rem;'>📊 风险预测与分期结论</h5>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0; margin-bottom:8px; border-top:1px solid #D1D5DB;'>", unsafe_allow_html=True)
    
    final_stage = get_val("saved_ckm_stage", "待评估")
    final_cvd = get_val("saved_cvd_risk", None)
    final_kdigo = get_val("saved_kdigo_risk", "待评估")
    cvd_str = f"{round(final_cvd * 100, 2)}%" if final_cvd is not None else "参数未齐，未触发计算"
    
    st.markdown(f"""
    <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 12px 15px; border-radius: 6px; line-height:1.6; font-size:0.9rem;">
        <span style="margin-right: 20px;">🔹 <b>10年心血管疾病（CVD）风险估算值：</b> <span style="color:#0EA5E9; font-weight:bold;">{cvd_str}</span></span>
        <span>🔹 <b>慢性肾脏病（CKD）危险分层评级：</b> <span style="color:#F59E0B; font-weight:bold;">{final_kdigo}</span></span>
        <div style="background-color: #F0F4F8; padding: 8px; margin-top:10px; border-radius: 4px; text-align: center; font-size:1.1rem; font-weight:800; color:#1E3A8A;">
            最终评估结果：心血管-肾脏-代谢综合征（CKM）{final_stage}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 【核心修改点】使用原生的 HTML 按钮结合 JS 唤起系统打印 window.parent.print()
    st.markdown("""
    <br>
    <div class="no-print" style="display: flex; justify-content: space-between; align-items: center; gap: 20px;">
        <a href="javascript:void(0)" onclick="window.parent.postMessage({type: 'streamlit:rerun'}, '*');" 
           style="text-decoration:none; width:45%;">
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <script>
            function triggerPrint() {
                window.parent.focus();
                window.parent.print();
            }
        </script>
    """, unsafe_allow_html=True)

    c1, _, c2 = st.columns([4, 2, 4])
    with c1:
        if st.button("⬅️ 返回修改数据", use_container_width=True):
            st.session_state.page = "main"
            st.session_state.is_locked = False
            st.rerun()
    with c2:
        components.html(
            """
            <button id="print-btn-action" style="
                width: 100%;
                background-color: #FF4B4B;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: bold;
                height: 38px;
                transition: background-color 0.2s;
            ">
                🖨️ 立即打印
            </button>

            <script>
                document.getElementById('print-btn-action').addEventListener('click', function() {
                    // 1. 尝试直接唤起父级 Streamlit 窗口的打印预览
                    try {
                        window.parent.focus();
                        window.parent.print();
                    } catch (e) {
                        // 2. 如果遇到跨域安全限制，唤起当前上下文打印
                        window.focus();
                        window.print();
                    }
                });
            </script>
            """,
            height=45
        )
# ------- 路由C：主计算输入表单页 -------
else:
    st.markdown("### 📋 基础患者信息")
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    with r1_c1: name = st.text_input("姓名", placeholder="请输入患者姓名", key="input_name")
    with r1_c2: id_no = st.text_input("ID号", placeholder="请输入ID", key="input_id")
    with r1_c3: age = st.number_input("年龄", min_value=0, max_value=120, value=None, step=1, placeholder="请输入", key="input_age")
    with r1_c4: gender = st.selectbox("性别", ["男", "女"], index=None, placeholder="请选择", key="input_gender")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1: height = st.number_input("身高 (cm)", min_value=50.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="input_height")
    with r2_c2: weight = st.number_input("体重 (kg)", min_value=10.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="input_weight")
    
    h_val = st.session_state.get("input_height")
    w_val = st.session_state.get("input_weight")
    bmi = round(w_val / ((h_val / 100) ** 2), 2) if (h_val and h_val > 0 and w_val) else 0.0
    
    with r2_c3: st.metric(label="BMI (自动计算)", value=f"{bmi} kg/m²" if bmi > 0 else "待输入")
    with r2_c4: waist = st.number_input("腰围 (cm)", min_value=30.0, max_value=200.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="input_waist")

    g_val = st.session_state.get("input_gender")
    w_w_val = st.session_state.get("input_waist")
    
    fpg_input = get_val("lab_fpg")
    hba1c_input = get_val("lab_hba1c")
    h2pg_input = get_val("lab_2hpg")
    tc_input = get_val("lab_tc")
    ldl_input = get_val("lab_ldl")
    tg_input = get_val("lab_tg")
    hdl_input = get_val("lab_hdl")
    bnp_input = get_val("lab_bnp")
    ctni_input = get_val("lab_ctni")
    ctnt_input = get_val("lab_ctnt")

    calc_diabetes = ((fpg_input is not None and fpg_input >= 7.0) or (hba1c_input is not None and hba1c_input >= 6.5) or (h2pg_input is not None and h2pg_input >= 11.0))
    calc_lipid = ((tc_input is not None and tc_input >= 6.2) or (ldl_input is not None and ldl_input >= 4.2) or (tg_input is not None and tg_input >= 2.3) or (hdl_input is not None and hdl_input < 1.0))
    calc_pre_diabetes = ((fpg_input is not None and 5.6 <= fpg_input <= 6.99) or (hba1c_input is not None and 5.7 <= hba1c_input <= 6.4) or (h2pg_input is not None and 7.8 <= h2pg_input < 11.0))
    
    ctni_ng_l = ctni_input * 1000 if ctni_input is not None else 0.0
    ctnt_ng_l = ctnt_input * 1000 if ctnt_input is not None else 0.0
    calc_sub_hf = ((bnp_input is not None and bnp_input >= 125) or (g_val == "女" and ctnt_input is not None and ctnt_ng_l >= 14) or (g_val == "男" and ctnt_input is not None and ctnt_ng_l >= 22) or (g_val == "女" and ctni_input is not None and ctni_ng_l >= 10) or (g_val == "男" and ctni_input is not None and ctni_ng_l >= 12))

    # ==========================================
    # 第二部分：疾病史及危险因素
    # ==========================================
    st.markdown("### 🗂️ 疾病（史）及危险因素")
    if calc_diabetes: calc_pre_diabetes = False
    
    r4_cols = st.columns(4)
    with r4_cols[0]: has_diabetes = st.checkbox("糖尿病", value=calc_diabetes)
    with r4_cols[1]: has_pre_diabetes = st.checkbox("糖尿病前状态", value=calc_pre_diabetes)
    with r4_cols[2]: 
        has_htn = st.checkbox("高血压")
        has_anti_htn = st.checkbox("└── 抗高血压药物") if has_htn else False
    with r4_cols[3]: 
        has_lipid = st.checkbox("高脂血症", value=calc_lipid)
        has_statin = st.checkbox("└── 他汀类药物") if has_lipid else False

    metabolic_score = 0
    if (g_val == "男" and w_w_val and w_w_val >= 90) or (g_val == "女" and w_w_val and w_w_val >= 85): metabolic_score += 1
    if (h2pg_input is not None and h2pg_input >= 7.8) or calc_diabetes: metabolic_score += 1
    if has_htn: metabolic_score += 1
    if tg_input is not None and tg_input >= 1.7: metabolic_score += 1
    if hdl_input is not None and ((g_val == "男" and hdl_input < 1.04) or (g_val == "女" and hdl_input < 1.3)): metabolic_score += 1
    calc_metabolic = (metabolic_score >= 3)
    
    r4_cols_ext = st.columns(3)
    with r4_cols_ext[0]: has_ckd = st.checkbox("慢性肾脏病")
    with r4_cols_ext[1]: has_metabolic = st.checkbox("代谢综合征", value=calc_metabolic)
    with r4_cols_ext[2]: has_smoke = st.checkbox("吸烟史")

    # ==========================================
    # 第三部分：心血管疾病史
    # ==========================================
    st.markdown("### 🏥 心血管疾病")
    r5_c1, r5_c2, r5_c3, r5_c4, r5_c5 = st.columns(5)
    with r5_c1: has_chd = st.checkbox("冠心病")
    with r5_c2: has_af = st.checkbox("房颤")
    with r5_c3: has_stroke_history = st.checkbox("脑梗死")
    with r5_c4: has_hf = st.checkbox("心力衰竭")
    with r5_c5: has_pad = st.checkbox("外周血管疾病")

    r6_c1, r6_c2 = st.columns(2)
    with r6_c1: has_sub_hf_final = st.checkbox("亚临床心力衰竭", value=calc_sub_hf)
    with r6_c2: has_sub_cvd = st.checkbox("亚临床心血管系统疾病")

    # ==========================================
    # 第四部分：生理化验指标输入表单
    # ==========================================
    st.markdown("### 🧪 生理指标与检验结果")
    r3_col_a = st.columns(5)
    with r3_col_a[0]: sbp = st.number_input("收缩压(mmHg)", min_value=50, max_value=250, value=None, step=1, format="%d", placeholder="请输入", key="lab_sbp")
    with r3_col_a[1]: dbp = st.number_input("舒张压(mmHg)", min_value=30, max_value=150, value=None, step=1, format="%d", placeholder="请输入", key="lab_dbp")
    with r3_col_a[2]: fpg = st.number_input("空腹血糖(mmol/L)", min_value=1.0, max_value=30.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_fpg")
    with r3_col_a[3]: ppg_2h = st.number_input("餐后2小时血糖(mmol/L)", min_value=1.0, max_value=40.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_2hpg")
    with r3_col_a[4]: hba1c = st.number_input("糖化血红蛋白(%)", min_value=3.0, max_value=20.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="lab_hba1c")
    
    r3_col_b = st.columns(5)
    with r3_col_b[0]: tc = st.number_input("总胆固醇(mmol/L)", min_value=0.5, max_value=20.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_tc")
    with r3_col_b[1]: tg = st.number_input("甘油三酯(mmol/L)", min_value=0.1, max_value=30.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_tg")
    with r3_col_b[2]: ldl_c = st.number_input("低密度脂蛋白(mmol/L)", min_value=0.1, max_value=15.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_ldl")
    with r3_col_b[3]: hdl_c = st.number_input("高密度脂蛋白(mmol/L)", min_value=0.1, max_value=5.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_hdl")
    with r3_col_b[4]: nt_probnp = st.number_input("N末端B型脑钠肽前体(pg/mL)", min_value=0, max_value=50000, value=None, step=1, format="%d", placeholder="请输入", key="lab_bnp")
    
    r3_col_c = st.columns(5) 
    with r3_col_c[0]: scr_umol = st.number_input("肌酐(μmol/L)", min_value=5.0, max_value=3000.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="lab_scr")
    with r3_col_c[1]: cysc = st.number_input("胱抑素C(mg/L)", min_value=0.1, max_value=15.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_cysc")
    with r3_col_c[2]: uacr = st.number_input("尿微量白蛋白/肌酐比值(mg/g)", min_value=0.0, max_value=5000.0, value=None, step=1.0, format="%.2f", placeholder="请输入", key="lab_uacr")
    with r3_col_c[3]: raw_ctnt = st.number_input("肌钙蛋白T(ng/mL)", min_value=0.0, max_value=50.0, value=None, step=0.001, format="%.3f", placeholder="请输入", key="lab_ctnt")
    with r3_col_c[4]: raw_ctni = st.number_input("肌钙蛋白I(μg/L)", min_value=0.0, max_value=50.0, value=None, step=0.001, format="%.3f", placeholder="请输入", key="lab_ctni")

    st.markdown("<br>", unsafe_allow_html=True)

    r3_egfr_row = st.columns([1, 1]) 
    with r3_egfr_row[0]:
        egfr_method = st.selectbox("估算的肾小球滤过率（eGFR）", ["2021 CKD-EPI sCr-CysC (联合法)", "2021 CKD-EPI sCr (单肌酐法)"])

    # 计算 eGFR
    scr_val_safe = get_val("lab_scr")
    cysc_val_safe = get_val("lab_cysc")
    age_safe = get_val("input_age")
    
    egfr = None
    if scr_val_safe is not None and age_safe is not None and g_val is not None:
        if "sCr-CysC" in egfr_method and cysc_val_safe is None:
            egfr = None
        else:
            scr_mgdl = scr_val_safe / 88.4
            is_female = 1 if g_val == "女" else 0
            kappa = 0.7 if is_female else 0.9
            
            if "sCr-CysC" in egfr_method:
                mu, a2, b1, b2 = 135, -0.544, -0.323, -0.778
                a1 = -0.219 if is_female else -0.144
                d_val = 0.963 if is_female else 1.0
                scr_term = scr_mgdl / kappa
                a_coef = a1 if ((is_female and scr_mgdl <= 0.7) or (not is_female and scr_mgdl <= 0.9)) else a2
                part1 = (min(scr_term, 1) ** a_coef) * (max(scr_term, 1) ** a2)
                cysc_term = cysc_val_safe / 0.8
                b_coef = b1 if cysc_val_safe <= 0.8 else b2
                part2 = (min(cysc_term, 1) ** b1) * (max(cysc_term, 1) ** b2)
                egfr = mu * part1 * part2 * (0.9961 ** age_safe) * d_val
            else:
                mu, a2 = 142, -1.2
                a1 = -0.241 if is_female else -0.302
                d_val = 1.012 if is_female else 1.0
                scr_term = scr_mgdl / kappa
                a_coef = a1 if ((is_female and scr_mgdl <= 0.7) or (not is_female and scr_mgdl <= 0.9)) else a2
                part1 = (min(scr_term, 1) ** a_coef) * (max(scr_term, 1) ** a2)
                egfr = mu * part1 * (0.9938 ** age_safe) * d_val
            egfr = round(egfr, 2)
            
    with r3_egfr_row[1]:
        st.metric(label="eGFR (自动计算)", value=f"{egfr} ml/(min・1.73m²)" if egfr is not None else "待输入")

    # ==========================================
    # 第五部分：核心数据引擎计算
    # ==========================================
    st.markdown("### 📊 疾病风险预测与危险分层")

    if_diabetes = 1 if has_diabetes else 0
    if_smoke = 1 if has_smoke else 0
    if_anti_htn = 1 if has_anti_htn else 0
    if_statin = 1 if has_statin else 0
    
    cvd_risk = None
    tc_val = get_val("lab_tc")
    hdl_val = get_val("lab_hdl")
    sbp_val = get_val("lab_sbp")
    
    if (age_safe is not None and g_val is not None and tc_val is not None and hdl_val is not None and sbp_val is not None and egfr is not None):
        age_term = (age_safe - 55) / 10
        tc_hdl_term = tc_val - hdl_val - 3.5
        hdl_term = (hdl_val - 1.3) / 0.3
        sbp_min_term = (min(sbp_val, 110) - 110) / 20
        sbp_max_term = (max(sbp_val, 110) - 130) / 20
        egfr_min_term = (min(egfr, 60) - 60) / -15
        egfr_max_term = (max(egfr, 60) - 90) / -15

        if g_val == "女":
            log_odds = (-3.307728 + 0.7939329 * age_term + 0.0305239 * tc_hdl_term 
                        - 0.1606857 * hdl_term - 0.2394003 * sbp_min_term + 0.360078 * sbp_max_term 
                        + 0.8667604 * if_diabetes + 0.5360739 * if_smoke + 0.6045917 * egfr_min_term 
                        + 0.0433769 * egfr_max_term + 0.3151672 * if_anti_htn - 0.1477655 * if_statin 
                        - 0.0663612 * if_anti_htn * sbp_max_term + 0.1197879 * if_statin * tc_hdl_term 
                        - 0.0819715 * age_term * tc_hdl_term + 0.0306769 * age_term * hdl_term 
                        - 0.0946348 * age_term * sbp_max_term - 0.27057 * age_term * if_diabetes 
                        - 0.078715 * age_term * if_smoke - 0.1637806 * age_term * egfr_min_term)
        else:
            log_odds = (-3.031168 + 0.7688528 * age_term + 0.0736174 * tc_hdl_term 
                        - 0.0954431 * hdl_term - 0.4347345 * sbp_min_term + 0.3362658 * sbp_max_term 
                        + 0.7692857 * if_diabetes + 0.4386871 * if_smoke + 0.5378979 * egfr_min_term 
                        + 0.0164827 * egfr_max_term + 0.288879 * if_anti_htn - 0.1337349 * if_statin 
                        - 0.0475924 * if_anti_htn * sbp_max_term + 0.150273 * if_statin * tc_hdl_term 
                        - 0.0517874 * age_term * tc_hdl_term + 0.0191169 * age_term * hdl_term 
                        - 0.1049477 * age_term * sbp_max_term - 0.2251948 * age_term * if_diabetes 
                        - 0.0895067 * age_term * if_smoke - 0.1543702 * age_term * egfr_min_term)
        cvd_risk = np.exp(log_odds) / (1 + np.exp(log_odds))

    kdigo_risk = "未满足标准"
    uacr_val = get_val("lab_uacr")
    if egfr is not None and uacr_val is not None:
        if (egfr < 30) or (30 <= egfr < 45 and uacr_val >= 30) or (45 <= egfr < 60 and uacr_val >= 300) or (egfr >= 60 and uacr_val >= 300):
            kdigo_risk = "极高风险，肾病专科积极治疗"
        elif (30 <= egfr < 45) or (45 <= egfr < 60 and uacr_val >= 30):
            kdigo_risk = "高风险，需强化治疗"
        elif (45 <= egfr < 60) or (egfr >= 60 and uacr_val >= 30):
            kdigo_risk = "中风险，需启动治疗"
        elif egfr >= 60 and uacr_val < 30:
            kdigo_risk = "低风险，仅做常规筛查"

    ckm_stage = None
    if egfr is not None or cvd_risk is not None or kdigo_risk != "未满足标准" or any([has_chd, has_af, has_stroke_history, has_pad, has_hf, has_diabetes, has_lipid, has_htn, has_metabolic, has_ckd]):
        cond_stage_4 = (has_chd or has_af or has_stroke_history or has_pad or has_hf or (egfr is not None and egfr <= 15))
        cond_stage_3 = (has_sub_cvd or has_sub_hf_final or (cvd_risk is not None and cvd_risk >= 0.2) or kdigo_risk == "极高风险，肾病专科积极治疗")
        cond_stage_2 = (has_diabetes or has_lipid or has_htn or has_metabolic or has_ckd)
        waist_cond_1 = (g_val == "女" and w_w_val and w_w_val >= 80) or (g_val == "男" and w_w_val and w_w_val >= 90)
        cond_stage_1 = (bmi >= 23 or waist_cond_1 or has_pre_diabetes)
        waist_cond_0 = (g_val == "女" and w_w_val and w_w_val < 80) or (g_val == "男" and w_w_val and w_w_val < 90)
        cond_stage_0 = (bmi > 0 and bmi < 23 and waist_cond_0 and not (has_diabetes or has_lipid or has_ckd or has_sub_cvd or has_chd or has_stroke_history or has_af or has_hf))

        if cond_stage_4: ckm_stage = "4期"
        elif cond_stage_3: ckm_stage = "3期"
        elif cond_stage_2: ckm_stage = "2期"
        elif cond_stage_1: ckm_stage = "1期"
        elif cond_stage_0: ckm_stage = "0期"

    st.session_state.saved_ckm_stage = ckm_stage if ckm_stage else "待输入评估参数"
    st.session_state.saved_cvd_risk = cvd_risk
    st.session_state.saved_kdigo_risk = kdigo_risk

    if cvd_risk is not None: st.info(f"📈 **10年心血管疾病（CVD）风险** ➔ {round(cvd_risk * 100, 2)}%")
    else: st.info("📈 **10年心血管疾病（CVD）风险** ➔ 待输入完整参数后计算")

    if kdigo_risk != "未满足标准": st.warning(f"📋 **慢性肾脏病(CKD)危险分层** ➔ {kdigo_risk}")
    else: st.warning("📋 **慢性肾脏病(CKD)危险分层** ➔ 待输入完整肾功能指标及尿微量白蛋白/肌酐比值后计算")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background-color: #F0F4F8; padding: 12px 20px; border-radius: 8px; text-align: center;">
        <span style="font-size: 1.1rem; font-weight: bold; color: #4B5563;">最终评估结果：</span>
        <span style="font-size: 1.4rem; font-weight: 800; color: #1E3A8A; margin-left: 8px;">
            心血管-肾脏-代谢综合征（CKM）{st.session_state.saved_ckm_stage}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # 底部操作控制条
    st.markdown("<br><br>", unsafe_allow_html=True)
    f1, _, f2, _, f3 = st.columns([2, 3, 2, 3, 2])
    with f1:
        if st.button("← 返回欢迎首页"):
            st.session_state.is_locked = False
            st.session_state.page = "cover"
            st.rerun()
    with f2:
        if st.button("确认", type="primary", disabled=st.session_state.is_locked):
            st.session_state.is_locked = True
            st.rerun()
    with f3:
        if st.button("🖨️ 打印结果", disabled=not st.session_state.is_locked):
            st.session_state.p_name = get_val("input_name", "未填写")
            st.session_state.p_id = get_val("input_id", "未填写")
            st.session_state.p_age = get_val("input_age", "--")
            st.session_state.p_gender = get_val("input_gender", "--")
            
            st.session_state.p_sbp = get_val("lab_sbp")
            st.session_state.p_dbp = get_val("lab_dbp")
            st.session_state.p_fpg = get_val("lab_fpg")
            st.session_state.p_2hpg = get_val("lab_2hpg")
            st.session_state.p_hba1c = get_val("lab_hba1c")
            st.session_state.p_tc = get_val("lab_tc")
            st.session_state.p_tg = get_val("lab_tg")
            st.session_state.p_ldl = get_val("lab_ldl")
            st.session_state.p_hdl = get_val("lab_hdl")
            st.session_state.p_bnp = get_val("lab_bnp")
            st.session_state.p_scr = get_val("lab_scr")
            st.session_state.p_cysc = get_val("lab_cysc")
            st.session_state.p_uacr = get_val("lab_uacr")
            st.session_state.p_ctnt = get_val("lab_ctnt")
            st.session_state.p_ctni = get_val("lab_ctni")
            
            history_tags = []
            if has_diabetes: history_tags.append("糖尿病")
            if has_pre_diabetes: history_tags.append("糖尿病前状态")
            if has_htn: history_tags.append("高血压")
            if has_anti_htn: history_tags.append("抗高血压药物治疗")
            if has_lipid: history_tags.append("高脂血症")
            if has_statin: history_tags.append("他汀类药物治疗")
            if has_ckd: history_tags.append("慢性肾脏病")
            if has_metabolic: history_tags.append("代谢综合征")
            if has_smoke: history_tags.append("吸烟史")
            if has_chd: history_tags.append("冠心病")
            if has_af: history_tags.append("房颤")
            if has_stroke_history: history_tags.append("脑梗死")
            if has_hf: history_tags.append("心力衰竭")
            if has_pad: history_tags.append("外周血管疾病")
            if has_sub_hf_final: history_tags.append("亚临床心力衰竭")
            if has_sub_cvd: history_tags.append("亚临床心血管系统疾病")
            st.session_state.p_history_tags = history_tags

            st.session_state.page = "print_view"
            st.rerun()