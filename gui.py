import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.model import Node, Element
from core.solver import solve_structure

# ==========================================
# 1. 页面设置与全局 CSS
# ==========================================
st.set_page_config(page_title="Matrix Structural Solver", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif; }
    
    .block-container { padding-top: 1.5rem; max-width: 98%; }
    
    /* 🌟 输入框矩阵化 */
    .stNumberInput > div > div > input, .stSelectbox > div > div > select { 
        border-radius: 4px !important; 
        font-size: 0.95rem !important;
        padding: 4px 8px !important;
        border: 1px solid #e9ecef;
        background-color: #fcfcfc;
    }
    .stNumberInput > div > div > input:focus { background-color: #ffffff; border-color: #1f77b4; box-shadow: none; }
    label[data-testid="stWidgetLabel"] { display: none !important; }
    
    /* 🌟 彻底修复复选框居中问题 */
    div[data-testid="stCheckbox"] { 
        display: flex; 
        justify-content: center !important; /* 外部容器居中 */
        align-items: center !important; 
        padding-top: 6px; 
    }
    div[data-testid="stCheckbox"] label {
        width: auto !important; /* 剥夺内部标签的满宽属性 */
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* 表头色彩与层级 */
    .header-group {
        text-align: center; font-weight: 600; color: white;
        padding: 6px 0; border-radius: 4px 4px 0 0; font-size: 0.95rem;
    }
    .bg-coord { background-color: #34495e; } 
    .bg-const { background-color: #7f8c8d; } 
    .bg-loads { background-color: #c0392b; } 
    
    .table-subheader { 
        text-align: center; font-size: 0.8rem; color: #868e96; font-weight: 600;
        border-bottom: 2px solid #e9ecef; padding-bottom: 4px; margin-bottom: 8px; margin-top: 4px;
    }
    
    .row-badge {
        background-color: #f1f3f5; color: #343a40; font-weight: 700; font-size: 0.9rem;
        text-align: center; padding: 6px 0; border-radius: 4px; border-left: 4px solid #adb5bd;
        margin-top: 3px;
    }
    
    div[data-testid="column"] { padding: 0 4px !important; }
    hr.row-divider { margin: 4px 0 8px 0; border-color: #f8f9fa; }
    
    .section-title { 
        font-size: 1.15rem; font-weight: 700; 
        margin-bottom: 0.8rem; border-left: 4px solid #1f77b4; padding-left: 10px; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 状态管理
# ==========================================
if 'nodes_data' in st.session_state and isinstance(st.session_state['nodes_data'], pd.DataFrame):
    st.session_state['nodes_data'] = st.session_state['nodes_data'].to_dict('records')
if 'elems_data' in st.session_state and isinstance(st.session_state['elems_data'], pd.DataFrame):
    st.session_state['elems_data'] = st.session_state['elems_data'].to_dict('records')

if 'nodes_data' not in st.session_state:
    st.session_state['nodes_data'] = [
        {"ID": 1, "X": 0.0, "Y": 0.0, "固X": False, "固Y": True, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
        {"ID": 2, "X": 4.0, "Y": 0.0, "固X": False, "固Y": False, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
        {"ID": 3, "X": 8.0, "Y": 3.0, "固X": False, "固Y": True, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
        {"ID": 4, "X": 4.0, "Y": -4.0, "固X": True, "固Y": True, "固转": True, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
    ]

if 'elems_data' not in st.session_state:
    st.session_state['elems_data'] = [
        {"ID": 1, "起点": 1, "终点": 2, "EA": 1e12, "EI": 4.0, "Fx_i": 0.0, "Fy_i": 0.0, "Mz_i": 0.0, "Fx_j": 0.0, "Fy_j": 0.0, "Mz_j": 0.0},
        {"ID": 2, "起点": 2, "终点": 3, "EA": 1e12, "EI": 5.0, "Fx_i": 0.0, "Fy_i": 0.0, "Mz_i": 0.0, "Fx_j": 0.0, "Fy_j": 0.0, "Mz_j": 0.0},
        {"ID": 3, "起点": 2, "终点": 4, "EA": 1e12, "EI": 4.0, "Fx_i": 0.0, "Fy_i": 24.0, "Mz_i": 16.0, "Fx_j": 0.0, "Fy_j": 24.0, "Mz_j": -16.0},
    ]

if 'analysis_results' not in st.session_state: st.session_state['analysis_results'] = None

def delete_node(idx): 
    nid = st.session_state['nodes_data'][idx]['ID']
    st.session_state['nodes_data'].pop(idx)
    st.session_state['elems_data'] = [e for e in st.session_state['elems_data'] if e['起点'] != nid and e['终点'] != nid]
def delete_elem(idx): st.session_state['elems_data'].pop(idx)

# ==========================================
# 3. 顶部标题
# ==========================================
st.markdown("<h3 style='margin-bottom: 0;'>🏗️ Matrix Structural Solver Dashboard</h3>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

# ==========================================
# 4. 全局布局
# ==========================================
col_left, col_right = st.columns([1.6, 1.4], gap="large")

# ------------------------------------------
# 👈 左侧面板：数据输入矩阵
# ------------------------------------------
with col_left:
    # --- 🔴 节点 ---
    st.markdown("<div class='section-title'>📍 节点信息</div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='display: flex; width: 100%; gap: 4px;'>
            <div style='flex: 1;' ></div>
            <div style='flex: 2;' class='header-group bg-coord'>📍 坐标 (m)</div>
            <div style='flex: 3;' class='header-group bg-const'>🔒 支座约束</div>
            <div style='flex: 3.6;' class='header-group bg-loads'>🎯 节点集中荷载</div>
            <div style='flex: 0.8;' ></div>
        </div>
    """, unsafe_allow_html=True)
    
    node_widths = [1, 1, 1, 1, 1, 1, 1.2, 1.2, 1.2, 0.8]
    n_cols = st.columns(node_widths)
    headers = ["Node", "x", "y", "固定x", "固定y", "固定转角", "Fx (kN)", "Fy (kN)", "Mz (kN·m)", "操作"]
    for i, h in enumerate(headers): n_cols[i].markdown(f"<div class='table-subheader'>{h}</div>", unsafe_allow_html=True)
    
    for i, node in enumerate(st.session_state['nodes_data']):
        cols = st.columns(node_widths)
        cols[0].markdown(f"<div class='row-badge'>N{node['ID']}</div>", unsafe_allow_html=True)
        node['X'] = cols[1].number_input(f"nx{i}", value=float(node['X']), step=0.1, key=f"n_x_{i}", label_visibility="collapsed")
        node['Y'] = cols[2].number_input(f"ny{i}", value=float(node['Y']), step=0.1, key=f"n_y_{i}", label_visibility="collapsed")
        
        # 居中显示的勾选框
        node['固X'] = cols[3].checkbox(f"nfx{i}", value=bool(node['固X']), key=f"n_fx_{i}", label_visibility="collapsed")
        node['固Y'] = cols[4].checkbox(f"nfy{i}", value=bool(node['固Y']), key=f"n_fy_{i}", label_visibility="collapsed")
        node['固转'] = cols[5].checkbox(f"nfm{i}", value=bool(node['固转']), key=f"n_fm_{i}", label_visibility="collapsed")
        
        node['Fx'] = cols[6].number_input(f"nffx{i}", value=float(node['Fx']), step=1.0, key=f"n_ffx_{i}", label_visibility="collapsed")
        node['Fy'] = cols[7].number_input(f"nffy{i}", value=float(node['Fy']), step=1.0, key=f"n_ffy_{i}", label_visibility="collapsed")
        node['Mz'] = cols[8].number_input(f"nffm{i}", value=float(node['Mz']), step=1.0, key=f"n_ffm_{i}", label_visibility="collapsed")
        if cols[9].button("✖", key=f"ndel_{i}"):
            delete_node(i); st.rerun()
        st.markdown("<hr class='row-divider'>", unsafe_allow_html=True)

    if st.button("➕ 增加节点 (Add Node)", key="add_node_row"):
        new_id = max([n['ID'] for n in st.session_state['nodes_data']] + [0]) + 1
        st.session_state['nodes_data'].append({"ID": new_id, "X": 0.0, "Y": 0.0, "固X": False, "固Y": False, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0})
        st.rerun()

    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)

    # --- 🔵 单元 ---
    st.markdown("<div class='section-title'>🔗 单元信息</div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='display: flex; width: 100%; gap: 4px;'>
            <div style='flex: 0.8;' ></div>
            <div style='flex: 2;' class='header-group bg-coord'> 连接节点</div>
            <div style='flex: 2;' class='header-group bg-const'> 材料属性</div>
            <div style='flex: 3.3;' class='header-group bg-loads'>i 端等效节点荷载</div>
            <div style='flex: 3.3;' class='header-group bg-loads'>j 端等效节点荷载</div>
            <div style='flex: 0.8;' ></div>
        </div>
    """, unsafe_allow_html=True)
    
    # 🌟 修改：加入详细单位，微调列宽避免挤压
    elem_widths = [0.8, 1, 1, 1.2, 1.2, 1.1, 1.1, 1.3, 1.1, 1.1, 1.3, 0.8]
    e_cols = st.columns(elem_widths)
    # 🌟 修改：加入单位
    e_headers = ["Elem", "起(i)", "终(j)", "EA (kN)", "EI (kN·m²)", "Fxi (kN)", "Fyi (kN)", "Mzi (kN·m)", "Fxj (kN)", "Fyj (kN)", "Mzj (kN·m)", "操作"]
    for i, h in enumerate(e_headers): e_cols[i].markdown(f"<div class='table-subheader'>{h}</div>", unsafe_allow_html=True)
    
    avail_node_ids = [n['ID'] for n in st.session_state['nodes_data']]
    
    for i, elem in enumerate(st.session_state['elems_data']):
        cols = st.columns(elem_widths)
        cols[0].markdown(f"<div class='row-badge' style='border-color: #1f77b4;'>E{elem['ID']}</div>", unsafe_allow_html=True)
        
        idx_i = avail_node_ids.index(elem['起点']) if elem['起点'] in avail_node_ids else 0
        idx_j = avail_node_ids.index(elem['终点']) if elem['终点'] in avail_node_ids else 0
        
        elem['起点'] = cols[1].selectbox(f"esi{i}", avail_node_ids, index=idx_i, key=f"e_si_{i}", label_visibility="collapsed")
        elem['终点'] = cols[2].selectbox(f"esj{i}", avail_node_ids, index=idx_j, key=f"e_sj_{i}", label_visibility="collapsed")
        elem['EA'] = cols[3].number_input(f"eea{i}", value=float(elem['EA']), format="%.0e", key=f"e_ea_{i}", label_visibility="collapsed")
        elem['EI'] = cols[4].number_input(f"eei{i}", value=float(elem['EI']), key=f"e_ei_{i}", label_visibility="collapsed")
        
        elem['Fx_i'] = cols[5].number_input(f"fxi{i}", value=float(elem['Fx_i']), key=f"e_fxi_{i}", label_visibility="collapsed")
        elem['Fy_i'] = cols[6].number_input(f"fyi{i}", value=float(elem['Fy_i']), key=f"e_fyi_{i}", label_visibility="collapsed")
        elem['Mz_i'] = cols[7].number_input(f"mzi{i}", value=float(elem['Mz_i']), key=f"e_mzi_{i}", label_visibility="collapsed")
        elem['Fx_j'] = cols[8].number_input(f"fxj{i}", value=float(elem['Fx_j']), key=f"e_fxj_{i}", label_visibility="collapsed")
        elem['Fy_j'] = cols[9].number_input(f"fyj{i}", value=float(elem['Fy_j']), key=f"e_fyj_{i}", label_visibility="collapsed")
        elem['Mz_j'] = cols[10].number_input(f"mzj{i}", value=float(elem['Mz_j']), key=f"e_mzj_{i}", label_visibility="collapsed")
        
        if cols[11].button("✖", key=f"edel_{i}"):
            delete_elem(i); st.rerun()
        st.markdown("<hr class='row-divider'>", unsafe_allow_html=True)

    if st.button("➕ 增加单元 (Add Element)", key="add_elem_row"):
        if len(avail_node_ids) >= 2:
            new_id = max([e['ID'] for e in st.session_state['elems_data']] + [0]) + 1
            st.session_state['elems_data'].append({"ID": new_id, "起点": avail_node_ids[0], "终点": avail_node_ids[1], "EA": 1e12, "EI": 1.0, "Fx_i": 0.0, "Fy_i": 0.0, "Mz_i": 0.0, "Fx_j": 0.0, "Fy_j": 0.0, "Mz_j": 0.0})
            st.rerun()

    # 🚀 求解计算
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
    if st.button("🚀 执行矩阵位移法求解 (Solve Structure)", type="primary", use_container_width=True):
        nodes_dict_intern = {int(n['ID']): Node(int(n['ID']), n['X'], n['Y'], [n['固X'], n['固Y'], n['固转']], [n['Fx'], n['Fy'], n['Mz']]) for n in st.session_state['nodes_data']}
        elems_list_intern = []
        for e in st.session_state['elems_data']:
            try: elems_list_intern.append(Element(int(e['ID']), nodes_dict_intern[e['起点']], nodes_dict_intern[e['终点']], e['EA'], e['EI'], [e['Fx_i'], e['Fy_i'], e['Mz_i'], e['Fx_j'], e['Fy_j'], e['Mz_j']]))
            except: pass
        
        try:
            U_total, forces = solve_structure(nodes_dict_intern, elems_list_intern)
            
            df_disp = pd.DataFrame([{"Node": f"N{nid}", "Ux (m)": U_total[n.dof[0]], "Uy (m)": U_total[n.dof[1]], "θz (rad)": U_total[n.dof[2]]} for nid, n in nodes_dict_intern.items()])
            df_disp.set_index("Node", inplace=True)

            force_data = []
            for eid, res in forces.items():
                force_data.append({"Elem": f"E{eid}", "Loc": "起点(i)", "N 轴力(kN)": res['local_i'][0], "V 剪力(kN)": res['local_i'][1], "M 弯矩(kN·m)": res['local_i'][2]})
                force_data.append({"Elem": f"E{eid}", "Loc": "终点(j)", "N 轴力(kN)": res['local_j'][0], "V 剪力(kN)": res['local_j'][1], "M 弯矩(kN·m)": res['local_j'][2]})
            df_force = pd.DataFrame(force_data).sort_values(by=["Elem", "Loc"])
            df_force.set_index(["Elem", "Loc"], inplace=True) 

            st.session_state['analysis_results'] = {'disp': df_disp, 'force': df_force}
            st.rerun()
        except Exception as e:
            st.error(f"❌ 求解失败，请检查模型约束。详细错误: {str(e)}")


# ------------------------------------------
# 👉 右侧面板：拓扑图 + 结果报告
# ------------------------------------------
with col_right:
    
    st.markdown("<div class='section-title'> 结构示意图</div>", unsafe_allow_html=True)
    fig = go.Figure()
    nodes_dict_intern = {int(n["ID"]): Node(int(n["ID"]), n["X"], n["Y"], [], []) for n in st.session_state['nodes_data']}
    
    for e in st.session_state['elems_data']:
        try:
            ni = nodes_dict_intern[e['起点']]; nj = nodes_dict_intern[e['终点']]
            fig.add_trace(go.Scatter(x=[ni.x, nj.x], y=[ni.y, nj.y], mode='lines', line=dict(color='#1f77b4', width=3), hoverinfo='none', showlegend=False))
            fig.add_trace(go.Scatter(x=[(ni.x+nj.x)/2], y=[(ni.y+nj.y)/2], mode='text', text=[f"<b>E{e['ID']}</b>"], textposition="top center", textfont=dict(color='#0984e3', size=15), showlegend=False))
        except: pass

    if nodes_dict_intern:
        nx = [n.x for n in nodes_dict_intern.values()]; ny = [n.y for n in nodes_dict_intern.values()]; nt = [f"N{nid}" for nid in nodes_dict_intern.keys()]
        fig.add_trace(go.Scatter(x=nx, y=ny, mode='markers+text', marker=dict(color='#d62728', size=10, line=dict(color='white', width=1)), text=nt, textposition="top right", textfont=dict(color='#343a40', size=15, weight="bold"), hoverinfo='none', showlegend=False))

    fig.update_layout(
        template="plotly_white", margin=dict(l=20, r=20, t=10, b=10),
        xaxis=dict(showgrid=True, gridcolor='#e9ecef', mirror=True, ticks='outside', showline=True, linecolor='#adb5bd'),
        yaxis=dict(showgrid=True, gridcolor='#e9ecef', mirror=True, ticks='outside', showline=True, linecolor='#adb5bd', scaleanchor="x", scaleratio=1),
        plot_bgcolor='white', paper_bgcolor='white', dragmode='pan', height=380 
    )
    st.plotly_chart(fig, use_container_width=True, config={'displaylogo': False}, theme=None)

    st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 计算结果</div>", unsafe_allow_html=True)
    
    if st.session_state['analysis_results'] is not None:
        res = st.session_state['analysis_results']
        df_d = res['disp']; df_f = res['force']
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Max |Ux|", f"{df_d['Ux (m)'].abs().max() * 1000:.2f} mm")
        m2.metric("Max |Uy|", f"{df_d['Uy (m)'].abs().max() * 1000:.2f} mm")
        m3.metric("Max |M|", f"{df_f['M 弯矩(kN·m)'].abs().max():.2f} kN·m")
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        st.markdown("<div style='font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; color: #1f77b4;'> 节点位移 [ U ]</div>", unsafe_allow_html=True)
        st.dataframe(df_d.style.set_properties(**{'font-size': '1.05rem', 'padding': '6px'}).format("{:.5e}"), use_container_width=True)
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        st.markdown("<div style='font-size: 1.05rem; font-weight: 600; margin-bottom: 8px; color: #d62728;'> 单元内力 [ f ]</div>", unsafe_allow_html=True)
        st.dataframe(df_f.style.set_properties(**{'font-size': '1.05rem', 'padding': '6px'}).format("{:.4f}"), use_container_width=True)
            
    else:
        st.info("👈 请在左侧输入模型数据，并点击【执行矩阵位移法求解】获取结果。")