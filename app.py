import streamlit as st
import numpy as np
import streamlit.components.v1 as components

# 1. 页面配置
st.set_page_config(page_title="心血管-肾脏-代谢综合征(CKM)自动分期决策系统", layout="wide")
st.markdown(
"""
<style>
@media print {
    /* 隐藏掉不想打印的元素 */
    .no-print { display: none !important; }
}
</style>
"""
, unsafe_allow_html=True
)

# 2. 状态初始化
if "page" not in st.session_state: st.session_state.page = "cover"
if "is_locked" not in st.session_state: st.session_state.is_locked = False
if "trigger_print" not in st.session_state: st.session_state.trigger_print = False

# 安全获取 Session State 数值的辅助函数（防止 NoneType 报错）
def get_val(key, default=None):
    val = st.session_state.get(key)
    return val if val is not None else default

# 3. 路由控制
if st.session_state.page == "cover":
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.7, 3.4, 0.7])
    with col2:
        st.markdown("<h1 style='text-align:center; color:#1E3A8A;'>心血管-肾脏-代谢综合征(CKM)自动分期决策系统</h1>", unsafe_allow_html=True)
        if st.button("进入系统 ➔", use_container_width=True, type="primary"):
            st.session_state.page = "main"
            st.rerun()
else:
    # ---------------- 主计算页 ----------------
    
    # ==========================================
    # 第一部分：基础患者信息
    # ==========================================
    st.markdown("### 📋 基础患者信息")
    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    with r1_c1: name = st.text_input("姓名", placeholder="请输入患者姓名")
    with r1_c2: id_no = st.text_input("ID号", placeholder="请输入登记ID")
    with r1_c3: age = st.number_input("年龄", min_value=0, max_value=120, value=None, step=1, placeholder="请输入", key="input_age")
    with r1_c4: gender = st.selectbox("性别", ["男", "女"], index=None, placeholder="请选择", key="input_gender")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1: height = st.number_input("身高 (cm)", min_value=50.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="input_height")
    with r2_c2: weight = st.number_input("体重 (kg)", min_value=10.0, max_value=250.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="input_weight")
    
    # 安全计算 BMI
    h_val = st.session_state.get("input_height")
    w_val = st.session_state.get("input_weight")
    bmi = round(w_val / ((h_val / 100) ** 2), 2) if (h_val and h_val > 0 and w_val) else 0.0
    
    with r2_c3: st.metric(label="BMI (自动计算)", value=f"{bmi} kg/m²" if bmi > 0 else "待输入")
    with r2_c4: waist = st.number_input("腰围 (cm)", min_value=30.0, max_value=200.0, value=None, step=0.1, format="%.1f", placeholder="请输入", key="input_waist")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 读取/预计算下方实验室化验的联动逻辑状态（修复高脂血症与性别无条件偶联Bug）
    # ==========================================
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

    calc_diabetes = (
        (fpg_input is not None and fpg_input >= 7.0) or 
        (hba1c_input is not None and hba1c_input >= 6.5) or 
        (h2pg_input is not None and h2pg_input >= 11.0)
    )
    
    # 纯化验值判定高脂血症，解除性别强制兜底默认
    calc_lipid = (
        (tc_input is not None and tc_input >= 6.2) or 
        (ldl_input is not None and ldl_input >= 4.2) or 
        (tg_input is not None and tg_input >= 2.3) or 
        (hdl_input is not None and hdl_input < 1.0)
    )
    
    calc_pre_diabetes = (
        (fpg_input is not None and 5.6 <= fpg_input <= 6.99) or 
        (hba1c_input is not None and 5.7 <= hba1c_input <= 6.4) or 
        (h2pg_input is not None and 7.8 <= h2pg_input < 11.0)
    )
    
    # 自动计算肌钙蛋白换算单位
    ctni_ng_l = ctni_input * 1000 if ctni_input is not None else 0.0
    ctnt_ng_l = ctnt_input * 1000 if ctnt_input is not None else 0.0
    calc_sub_hf = (
        (bnp_input is not None and bnp_input >= 125) or 
        (g_val == "女" and ctnt_input is not None and ctnt_ng_l >= 14) or 
        (g_val == "男" and ctnt_input is not None and ctnt_ng_l >= 22) or 
        (g_val == "女" and ctni_input is not None and ctni_ng_l >= 10) or 
        (g_val == "男" and ctni_input is not None and ctni_ng_l >= 12)
    )

    # ==========================================
    # 第二部分：疾病史及危险因素
    # ==========================================
    st.markdown("### 🗂️ 疾病（史）及危险因素")
    if calc_diabetes:
     calc_pre_diabetes = False
    
    r4_cols = st.columns(4)
    with r4_cols[0]: has_diabetes = st.checkbox("糖尿病", value=calc_diabetes)
    with r4_cols[1]: has_pre_diabetes = st.checkbox("糖尿病前状态", value=calc_pre_diabetes)
    with r4_cols[2]: 
        has_htn = st.checkbox("高血压")
        has_anti_htn = st.checkbox("└── 抗高血压药物") if has_htn else False
    with r4_cols[3]: 
        has_lipid = st.checkbox("高脂血症", value=calc_lipid)
        has_statin = st.checkbox("└── 他汀类药物") if has_lipid else False

    # 代谢综合征自动判定（5选3）
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

    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 第三部分：心血管疾病史
    # ==========================================
    st.markdown("### 🏥 心血管疾病")
    
    r5_c1, r5_c2, r5_c3, r5_c4, r5_c5 = st.columns(5)
    with r5_c1: has_chd = st.checkbox("冠心病")
    with r5_c2: has_af = st.checkbox("房颤")
    with r5_c3: has_stroke_history = st.checkbox("脑梗")
    with r5_c4: has_hf = st.checkbox("心力衰竭")
    with r5_c5: has_pad = st.checkbox("外周血管疾病")

    r6_c1, r6_c2 = st.columns(2)
    with r6_c1: has_sub_hf_final = st.checkbox("亚临床心力衰竭", value=calc_sub_hf)
    with r6_c2: has_sub_cvd = st.checkbox("亚临床心血管系统疾病")


    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # 第四部分：实验室化验与生理指标
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
    with r3_col_c[0]: scr_umol = st.number_input("肌酐(μmol/L)", min_value=5, max_value=3000, value=None, step=1, format="%d", placeholder="请输入", key="lab_scr")
    with r3_col_c[1]: cysc = st.number_input("胱抑素C(mg/L)", min_value=0.1, max_value=15.0, value=None, step=0.01, format="%.2f", placeholder="请输入", key="lab_cysc")
    with r3_col_c[2]: uacr = st.number_input("尿微量白蛋白/肌酐比值(mg/g)", min_value=0.0, max_value=5000.0, value=None, step=1.0, format="%.2f", placeholder="请输入", key="lab_uacr")
    with r3_col_c[3]: raw_ctnt = st.number_input("肌钙蛋白T(ng/mL)", min_value=0.0, max_value=50.0, value=None, step=0.001, format="%.3f", placeholder="请输入", key="lab_ctnt")
    with r3_col_c[4]: raw_ctni = st.number_input("肌钙蛋白I(μg/L)", min_value=0.0, max_value=50.0, value=None, step=0.001, format="%.3f", placeholder="请输入", key="lab_ctni")

    st.markdown("<br>", unsafe_allow_html=True)

    # eGFR 计算配置及展示行
    r3_egfr_row = st.columns([2, 1]) 
    with r3_egfr_row[0]:
        egfr_method = st.selectbox(
        "估算的肾小球滤过率（eGFR）", 
            ["2021 CKD-EPI sCr-CysC (联合法)", "2021 CKD-EPI sCr (单肌酐法)"],
        help="点击下拉箭头展开公式选项，选中后系统自动加载对应计算逻辑。"
        )

    # 动态安全计算 eGFR（参数未配齐则初始值为空）
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

    st.markdown("### 📊 疾病风险预测与危险分层")

    # ==========================================
    # 公式1：10年CVD风险引擎核心计算（缺少计算参数时初始值为空）
    # ==========================================
    if_diabetes = 1 if has_diabetes else 0
    if_smoke = 1 if has_smoke else 0
    if_anti_htn = 1 if has_anti_htn else 0
    if_statin = 1 if has_statin else 0
    
    cvd_risk = None
    tc_val = get_val("lab_tc")
    hdl_val = get_val("lab_hdl")
    sbp_val = get_val("lab_sbp")
    
    if (age_safe is not None and g_val is not None and tc_val is not None and 
        hdl_val is not None and sbp_val is not None and egfr is not None):
        
        age_term = (age_safe - 55) / 10
        tc_hdl_term = tc_val - hdl_val - 3.5
        hdl_term = (hdl_val - 1.3) / 0.3
        sbp_min_term = (min(sbp_val, 110) - 110) / 20
        sbp_max_term = (max(sbp_val, 110) - 130) / 20
        egfr_min_term = (min(egfr, 60) - 60) / -15
        egfr_max_term = (max(egfr, 60) - 90) / -15

        if g_val == "女":
            log_odds = (-3.307728 + 0.7939329 * age_term + 0.0305239 * tc_hdl_term - 0.1606857 * hdl_term 
                        - 0.2394003 * sbp_min_term + 0.360078 * sbp_max_term + 0.8667604 * if_diabetes 
                        + 0.5360739 * if_smoke + 0.6045917 * egfr_min_term + 0.0433769 * egfr_max_term 
                        + 0.3151672 * if_anti_htn - 0.1477655 * if_statin - 0.0663612 * if_anti_htn * sbp_max_term 
                        + 0.1197879 * if_statin * tc_hdl_term - 0.0819715 * age_term * tc_hdl_term 
                        + 0.0306769 * age_term * hdl_term - 0.0946348 * age_term * sbp_max_term 
                        - 0.27057 * age_term * if_diabetes - 0.078715 * age_term * if_smoke 
                        - 0.1637806 * age_term * egfr_min_term)
        else:
            log_odds = (-3.031168 + 0.7688528 * age_term + 0.0736174 * tc_hdl_term - 0.0954431 * hdl_term 
                        - 0.4347345 * sbp_min_term + 0.3362658 * sbp_max_term + 0.7692857 * if_diabetes 
                        + 0.4386871 * if_smoke + 0.5378979 * egfr_min_term + 0.0164827 * egfr_max_term 
                        + 0.288879 * if_anti_htn - 0.1337349 * if_statin - 0.0475924 * if_anti_htn * sbp_max_term 
                        + 0.150273 * if_statin * tc_hdl_term - 0.0517874 * age_term * tc_hdl_term 
                        + 0.0191169 * age_term * hdl_term - 0.1049477 * age_term * sbp_max_term 
                        - 0.2251948 * age_term * if_diabetes - 0.0895067 * age_term * if_smoke 
                        - 0.1543702 * age_term * egfr_min_term)
                        
        cvd_risk = np.exp(log_odds) / (1 + np.exp(log_odds))

    # ==========================================
    # 公式6：KDIGO 风险评级模型（缺少计算参数时初始值为空）
    # ==========================================
    kdigo_risk = None
    uacr_val = get_val("lab_uacr")
    kdigo_risk = None
    uacr_val = get_val("lab_uacr")
    
    if egfr is not None and uacr_val is not None:
        # 1. 极高风险：所有涵盖严重病变的情况（合并同类项，逻辑覆盖所有 >= 300 或 < 30 的情况）
        if (egfr < 30) or (30 <= egfr < 45 and uacr_val >= 30) or (45 <= egfr < 60 and uacr_val >= 300) or (egfr >= 60 and uacr_val >= 300):
            kdigo_risk = "极高风险，肾病专科积极治疗"
        elif (30 <= egfr < 45) or (45 <= egfr < 60 and uacr_val >= 30):
            kdigo_risk = "高风险，需强化治疗"
        elif (45 <= egfr < 60) or (egfr >= 60 and uacr_val >= 30):
            kdigo_risk = "中风险，需启动治疗"
        elif egfr >= 60 and uacr_val < 30:
            kdigo_risk = "低风险，仅做常规筛查"
        else:
            kdigo_risk = "未满足标准"

    # ==========================================
    # 公式10：核心决策引擎 —— CKM分期递进逻辑（参数不齐时初始值为空）
    # ==========================================
    ckm_stage = None
    if egfr is not None or cvd_risk is not None or kdigo_risk is not None or any([has_chd, has_af, has_stroke_history, has_pad, has_hf, has_diabetes, has_lipid, has_htn, has_metabolic, has_ckd]):
        cond_stage_4 = (has_chd or has_af or has_stroke_history or has_pad or has_hf or (egfr is not None and egfr <= 15))
        cond_stage_3 = (has_sub_cvd or has_sub_hf_final or (cvd_risk is not None and cvd_risk >= 0.2) or kdigo_risk == "极高风险，积极治疗并转诊肾病专科")
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
        else: ckm_stage = None

    # ==========================================
    # 看板结果展示
    # ==========================================
    if cvd_risk is not None:
        st.info(f"📈 **10年心血管疾病（CVD）风险** ➔ {round(cvd_risk * 100, 2)}%")
    else:
        st.info("📈 **10年心血管疾病（CVD）风险** ➔ 待输入完整参数后计算")

    if kdigo_risk is not None:
        st.warning(f"📋 **慢性肾脏病(CKD)危险分层** ➔ {kdigo_risk}")
    else:
        st.warning("📋 **慢性肾脏病(CKD)危险分层** ➔ 待输入完整肾功能指标及尿微量白蛋白/肌酐比值后计算")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background-color: #F0F4F8; padding: 12px 20px; border-radius: 8px; text-align: center;">
        <span style="font-size: 1.1rem; font-weight: bold; color: #4B5563;">最终评估结果：</span>
        <span style="font-size: 1.4rem; font-weight: 800; color: #1E3A8A; margin-left: 8px;">
            {f"心血管-肾脏-代谢综合征（CKM）{ckm_stage}" if ckm_stage else "待输入评估参数"}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # 底部操作栏
if st.session_state.get("page") != "cover":
    st.markdown("<br><br>", unsafe_allow_html=True)

    # 创建 5 列，其中第 2 列和第 4 列作为弹性空白占位
    st.markdown('<div class="no-print">', unsafe_allow_html=True)
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
            st.session_state.trigger_print = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.trigger_print:
        components.html("""<script>window.print();</script>""", height=0)
        st.session_state.trigger_print = False