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
    
    .block-container { padding-top: 3rem; max-width: 98%; }
    
    [data-testid="stDataFrame"] { border: 1px solid #e9ecef; border-radius: 6px; }
    
    .section-title { 
        font-size: 1.15rem; font-weight: 700; 
        margin-bottom: 0.8rem; border-left: 4px solid #1f77b4; padding-left: 10px; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 状态管理
# ==========================================
if 'df_nodes' not in st.session_state:
    st.session_state.df_nodes = pd.DataFrame([
        {"ID": 1, "X": 0.0, "Y": 0.0, "固X": False, "固Y": True, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
        {"ID": 2, "X": 4.0, "Y": 0.0, "固X": False, "固Y": False, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
        {"ID": 3, "X": 8.0, "Y": 3.0, "固X": False, "固Y": True, "固转": False, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
        {"ID": 4, "X": 4.0, "Y": -4.0, "固X": True, "固Y": True, "固转": True, "Fx": 0.0, "Fy": 0.0, "Mz": 0.0},
    ])

if 'df_elems' not in st.session_state:
    st.session_state.df_elems = pd.DataFrame([
        {"ID": 1, "起点": 1, "终点": 2, "EA": 1e12, "EI": 4.0, "Fx_i": 0.0, "Fy_i": 0.0, "Mz_i": 0.0, "Fx_j": 0.0, "Fy_j": 0.0, "Mz_j": 0.0},
        {"ID": 2, "起点": 2, "终点": 3, "EA": 1e12, "EI": 5.0, "Fx_i": 0.0, "Fy_i": 0.0, "Mz_i": 0.0, "Fx_j": 0.0, "Fy_j": 0.0, "Mz_j": 0.0},
        {"ID": 3, "起点": 2, "终点": 4, "EA": 1e12, "EI": 4.0, "Fx_i": 0.0, "Fy_i": 24.0, "Mz_i": 16.0, "Fx_j": 0.0, "Fy_j": 24.0, "Mz_j": -16.0},
    ])

if 'analysis_results' not in st.session_state: st.session_state['analysis_results'] = None

# ==========================================
# 3. 顶部标题
# ==========================================
st.markdown("<h3 style='margin-bottom: 0;'>🏗️ Matrix Structural Solver Dashboard</h3>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 0.5rem; margin-bottom: 1rem;'>", unsafe_allow_html=True)

# ==========================================
# 4. 全局布局
# ==========================================
# 🌟 核心修改：大幅加宽左侧面板（比例改为 2.2 : 1.0）
col_left, col_right = st.columns([2.2, 1.0], gap="large")

# ------------------------------------------
# 👈 左侧面板：原生可编辑表格 UI
# ------------------------------------------
with col_left:
    # --- 🔴 节点信息 ---
    st.markdown("<div class='section-title'>📍 节点信息</div>", unsafe_allow_html=True)
    st.caption("✨ 提示：直接点击单元格编辑。点击表格最下方可添加新行，选中行后按 Delete 键可删除。")
    
    edited_nodes = st.data_editor(
        st.session_state.df_nodes,
        num_rows="dynamic",     
        use_container_width=True,
        hide_index=True,        
        column_config={
            "ID": st.column_config.NumberColumn("Node", required=True, step=1, format="%d"),
            "X": st.column_config.NumberColumn("x (m)", default=0.0, format="%.2f"),
            "Y": st.column_config.NumberColumn("y (m)", default=0.0, format="%.2f"),
            "固X": st.column_config.CheckboxColumn("固定x"),
            "固Y": st.column_config.CheckboxColumn("固定y"),
            "固转": st.column_config.CheckboxColumn("固定转角"),
            "Fx": st.column_config.NumberColumn("Fx (kN)", default=0.0),
            "Fy": st.column_config.NumberColumn("Fy (kN)", default=0.0),
            "Mz": st.column_config.NumberColumn("Mz (kN·m)", default=0.0),
        },
        key="node_editor"
    )

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    # --- 🔵 单元信息 ---
    st.markdown("<div class='section-title'>🔗 单元信息</div>", unsafe_allow_html=True)
    
    valid_node_ids = edited_nodes['ID'].dropna().astype(int).astype(str).tolist() if not edited_nodes.empty else []

    edited_elems = st.data_editor(
        st.session_state.df_elems,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn("Elem", required=True, step=1, format="%d"),
            "起点": st.column_config.SelectboxColumn("起(i)", options=valid_node_ids, required=True),
            "终点": st.column_config.SelectboxColumn("终(j)", options=valid_node_ids, required=True),
            "EA": st.column_config.NumberColumn("EA (kN)", default=1e12, format="%.2e"),
            "EI": st.column_config.NumberColumn("EI (kN·m²)", default=1.0),
            "Fx_i": st.column_config.NumberColumn("Fxi (kN)", default=0.0),
            "Fy_i": st.column_config.NumberColumn("Fyi (kN)", default=0.0),
            "Mz_i": st.column_config.NumberColumn("Mzi (kN·m)", default=0.0),
            "Fx_j": st.column_config.NumberColumn("Fxj (kN)", default=0.0),
            "Fy_j": st.column_config.NumberColumn("Fyj (kN)", default=0.0),
            "Mz_j": st.column_config.NumberColumn("Mzj (kN·m)", default=0.0),
        },
        key="elem_editor"
    )

    # 🚀 求解计算
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)
    if st.button("🚀 执行矩阵位移法求解 (Solve Structure)", type="primary", use_container_width=True):
        try:
            df_n_clean = edited_nodes.dropna(subset=['ID']).fillna(0)
            df_e_clean = edited_elems.dropna(subset=['ID', '起点', '终点']).fillna(0)
            
            nodes_dict_intern = {}
            for _, r in df_n_clean.iterrows():
                nodes_dict_intern[int(r["ID"])] = Node(int(r["ID"]), float(r["X"]), float(r["Y"]), [bool(r["固X"]), bool(r["固Y"]), bool(r["固转"])], [float(r["Fx"]), float(r["Fy"]), float(r["Mz"])])
            
            elems_list_intern = []
            for _, r in df_e_clean.iterrows():
                ni = nodes_dict_intern.get(int(r["起点"]))
                nj = nodes_dict_intern.get(int(r["终点"]))
                if ni and nj:
                    elems_list_intern.append(Element(int(r["ID"]), ni, nj, float(r["EA"]), float(r["EI"]), [float(r["Fx_i"]), float(r["Fy_i"]), float(r["Mz_i"]), float(r["Fx_j"]), float(r["Fy_j"]), float(r["Mz_j"])]))
            
            if not elems_list_intern:
                st.warning("⚠️ 模型中暂无有效的单元连接，请检查输入。")
            else:
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
                
                st.session_state.df_nodes = df_n_clean
                st.session_state.df_elems = df_e_clean
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ 求解失败，请检查模型约束。详细错误: {str(e)}")


# ------------------------------------------
# 👉 右侧面板：拓扑图 + 结果报告
# ------------------------------------------
with col_right:
    
    st.markdown("<div class='section-title'> 结构示意图</div>", unsafe_allow_html=True)
    fig = go.Figure()
    
    current_nodes = edited_nodes.dropna(subset=['ID']).fillna(0)
    current_elems = edited_elems.dropna(subset=['ID', '起点', '终点']).fillna(0)
    
    nodes_dict_viz = {int(r["ID"]): Node(int(r["ID"]), float(r["X"]), float(r["Y"]), [], []) for _, r in current_nodes.iterrows()}
    
    for _, r in current_elems.iterrows():
        try:
            ni = nodes_dict_viz[int(r['起点'])]; nj = nodes_dict_viz[int(r['终点'])]
            fig.add_trace(go.Scatter(x=[ni.x, nj.x], y=[ni.y, nj.y], mode='lines', line=dict(color='#1f77b4', width=3), hoverinfo='none', showlegend=False))
            fig.add_trace(go.Scatter(x=[(ni.x+nj.x)/2], y=[(ni.y+nj.y)/2], mode='text', text=[f"<b>E{int(r['ID'])}</b>"], textposition="top center", textfont=dict(color='#0984e3', size=15), showlegend=False))
        except: pass

    if nodes_dict_viz:
        nx = [n.x for n in nodes_dict_viz.values()]; ny = [n.y for n in nodes_dict_viz.values()]; nt = [f"N{nid}" for nid in nodes_dict_viz.keys()]
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
        st.info("👈 请在左侧表格中输入或修改模型数据，并点击【求解】获取结果。")
