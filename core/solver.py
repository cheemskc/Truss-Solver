import numpy as np
from .model import Node, Element  # 把我们刚才写的两个类导入进来

# 这是一个函数 (def)，接收所有节点(字典形式)和所有单元(列表形式)
def solve_structure(nodes_dict, elems_list):
    
    # 算一下总共有多少个自由度：节点数量乘以 3
    n_dof = len(nodes_dict) * 3
    
    # np.zeros 会创建一个全是 0 的大矩阵。
    # K_global 是总刚度矩阵 (n_dof 行，n_dof 列)
    K_global = np.zeros((n_dof, n_dof))
    # P_global 是总载荷向量 (n_dof 个元素的数组)
    P_global = np.zeros(n_dof)

    # ==========================================
    # 步骤 1：拼装节点集中力
    # ==========================================
    # 遍历每一个节点 (node)
    for node in nodes_dict.values():
        # 把节点的 F [Fx, Fy, Mz] 塞进总载荷向量对应的位置
        # node.dof[0]:node.dof[2]+1 这种写法叫“切片”，意思是提取第0、1、2个位置
        P_global[node.dof[0]:node.dof[2]+1] = node.F

    # ==========================================
    # 步骤 2：拼装总刚度矩阵 和 等效节点力
    # ==========================================
    # 遍历每一根杆件 (el)
    for el in elems_list:
        k_glob = el.get_k_glob()  # 获取这根杆件的全局刚度矩阵 (6x6)
        T = el.get_T()            # 获取转换矩阵
        
        # 把这根杆件连接的两个节点的自由度编号拼在一起 (一共6个数字)
        # 比如连着节点1和2，dofs 就是 [0, 1, 2, 3, 4, 5]
        dofs = el.i.dof + el.j.dof
        
        # 🌟 物理核心：求等效节点力 (ENL)
        ENL_loc = -el.FEF             # 局部等效力 = - 固端内力 (反作用力)
        ENL_glob = T.T @ ENL_loc      # 把局部的力转到全局坐标系下
        
        # 嵌套循环 (6x6)，把这根杆件的“小矩阵”叠加上“大矩阵”里去
        for r in range(6):
            # 把等效节点力加到总载荷向量里
            P_global[dofs[r]] += ENL_glob[r]  
            for c in range(6):
                # 把刚度值累加到总刚度矩阵对应的格子里 (矩阵组装原理)
                K_global[dofs[r], dofs[c]] += k_glob[r, c]

    # ==========================================
    # 步骤 3：处理支座约束，降维并求解位移
    # ==========================================
    free_dofs = [] # 创建一个空列表，用来装“没有被固定”的自由度编号
    
    for node in nodes_dict.values():
        # enumerate 会同时给你索引 i (0,1,2) 和内容 is_fixed (True/False)
        for i, is_fixed in enumerate(node.fix):
            if not is_fixed:  # 如果没有被固定 (False)
                free_dofs.append(node.dof[i]) # 就把这个自由度编号塞进列表里
    
    # 🌟 Python/Numpy 魔法：np.ix_ 
    # 它能直接把没有被固定的那些行和列“抽”出来，变成一个更小的可逆矩阵
    K_free = K_global[np.ix_(free_dofs, free_dofs)]
    P_free = P_global[free_dofs]

    # 线性代数求解核心：调用 numpy 的线性方程组求解器 (解 K * U = P)
    U_free = np.linalg.solve(K_free, P_free)
    
    # 准备一个全量位移向量 (全是0)，然后把刚才算出来的自由位移填回对应的洞里
    U_total = np.zeros(n_dof)
    U_total[free_dofs] = U_free

    # ==========================================
    # 步骤 4：根据位移反推杆件内部的真实受力
    # ==========================================
    forces_results = {}  # 创建一个空字典，用来存每根杆件的结果
    
    for el in elems_list:
        dofs = el.i.dof + el.j.dof
        u_glob = U_total[dofs]       # 抽出这根杆件两端的全局位移
        u_loc = el.get_T() @ u_glob  # 转成局部变形 (T * U)
        
        # 🌟 终极力学公式：局部内力 = 局部刚度 * 局部变形 + 固端内力
        f_loc = el.get_k_loc() @ u_loc + el.FEF
        
        # 按照你的要求，不经过任何正负号翻译，直接提取原生的局部坐标系受力
        Fx_i, Fy_i, Mz_i = f_loc[0], f_loc[1], f_loc[2]
        Fx_j, Fy_j, Mz_j = f_loc[3], f_loc[4], f_loc[5]
        
        # 把结果打包存进字典里返回
        forces_results[el.id] = {
            'local_i': (Fx_i, Fy_i, Mz_i),
            'local_j': (Fx_j, Fy_j, Mz_j)
        }
        
    return U_total, forces_results # 函数执行完毕，交出位移和内力成绩单