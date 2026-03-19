
import numpy as np
from core.model import Node, Element
from core.solver import solve_structure

def main():
    np.set_printoptions(precision=6, suppress=True)

    # 1. 定义节点 
    n1 = Node(1, 0.0, 0.0, [False, True, False],  [0.0, 0.0, 0.0])
    n2 = Node(2, 4.0, 0.0, [False, False, False], [0.0, 0.0, 0.0]) 
    n3 = Node(3, 8.0, 3.0, [False, True, False],  [0.0, 0.0, 0.0])
    n4 = Node(4, 4.0, -4.0, [True,True, True],  [0.0, 0.0, 0.0])
    nodes_dict = {1: n1, 2: n2, 3: n3, 4: n4}

    # 2. 输入固端内力 FEF
    
    fef_e1 = [0.0, 0.0, 0.0,   0.0, 0.0, 0.0]  
    fef_e2 = [0.0, 0.0, 0.0,   0.0, 0.0, 0.0] 
    fef_e3 = [0.0, 24, 16,   0.0, 24, -16]

    # 3. 定义单元
    e1 = Element(1, n1, n2, 1e12, 4.0, FEF=fef_e1)
    e2 = Element(2, n2, n3, 1e12, 5.0, FEF=fef_e2)
    e3 = Element(3, n2, n4, 1e12, 4.0, FEF=fef_e3)
    elems_list = [e1, e2, e3]

    # 求解与打印
    print("🚀 正在启动全自动载荷组装引擎...")
    U_total, forces = solve_structure(nodes_dict, elems_list)

    print("\n========== 📍 节点全量位移 ==========")
    for nid, node in nodes_dict.items():
        print(f"节点 {nid}: Ux = {U_total[node.dof[0]]:>10.6f}, Uy = {U_total[node.dof[1]]:>10.6f}, Th = {U_total[node.dof[2]]:>10.6f}")

    print("\n========== 🔪 单元杆端受力 (局部坐标系) ==========")
    for eid, res in forces.items():
        print(f"🔗 单元 {eid}:")
        print(f"   起点 👉 局部 Fx = {res['local_i'][0]:>9.4f}, 局部 Fy = {res['local_i'][1]:>9.4f}, 局部 Mz = {res['local_i'][2]:>9.4f}")
        print(f"   终点 👉 局部 Fx = {res['local_j'][0]:>9.4f}, 局部 Fy = {res['local_j'][1]:>9.4f}, 局部 Mz = {res['local_j'][2]:>9.4f}")
        print(f"   终点 👉 局部 Fx = {res['local_j'][0]:>9.4f}, 局部 Fy = {res['local_j'][1]:>9.4f}, 局部 Mz = {res['local_j'][2]:>9.4f}")

if __name__ == "__main__":
    main()