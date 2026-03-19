import numpy as np  # 导入 numpy 库，专门用来做矩阵和数组运算，我们给它起个小名叫 np
import math         # 导入 python 自带的数学库，用来算平方根、三角函数等

# ==========================================
# 📍 节点类 (Node)：定义结构中的连接点
# ==========================================
class Node:
    # __init__ 是 Python 的“构造函数”。当你创建一个新节点时，这段代码会自动运行
    def __init__(self, node_id, x, y, fix, F):
        self.id = node_id  # 把传进来的 node_id 存到节点自己的肚子里 (self 代表自己)
        self.x = x         # 节点的 X 坐标
        self.y = y         # 节点的 Y 坐标
        self.fix = fix     # 支座约束情况，比如 [False, True, False] 列表
        
        # 把传进来的外力列表 F 强制转换成 numpy 的小数数组，方便后续做数学运算
        self.F = np.array(F, dtype=float) 
        
        # 🌟 核心技巧：提前给节点分配好“自由度编号” (Degree of Freedom, DOF)
        # 每个节点有 3 个自由度 (X位移, Y位移, Z转角)
        # 如果节点 ID 是 1，编号就是 [0, 1, 2]；节点 2 就是 [3, 4, 5]
        # 在 Python 里，索引是从 0 开始的！
        self.dof = [(node_id-1)*3, (node_id-1)*3+1, (node_id-1)*3+2]

# ==========================================
# 🔗 单元类 (Element)：定义连接两个节点的杆件
# ==========================================
class Element:
    def __init__(self, elem_id, node_i, node_j, EA, EI, FEF):
        self.id = elem_id   # 单元的编号
        self.i = node_i     # 单元的起点 (这是一个 Node 对象)
        self.j = node_j     # 单元的终点 (这也是一个 Node 对象)
        self.EA = EA        # 轴向刚度
        self.EI = EI        # 抗弯刚度
        
        # 固端内力 (Fixed-End Forces)，转成 numpy 数组
        self.FEF = np.array(FEF, dtype=float) 
        
        # 计算杆件的几何属性
        dx = node_j.x - node_i.x  # 终点 X 减去 起点 X
        dy = node_j.y - node_i.y  # 终点 Y 减去 起点 Y
        
        # math.hypot 用来求直角三角形的斜边长，也就是杆件长度 L
        self.L = math.hypot(dx, dy) 
        
        # 算出杆件与全局 X 轴夹角的余弦 (c = cos) 和 正弦 (s = sin)
        self.c = dx / self.L
        self.s = dy / self.L

    # 定义一个方法，生成 6x6 的【局部坐标系】刚度矩阵 (k_loc)
    def get_k_loc(self):
        EA, EI, L = self.EA, self.EI, self.L  # 为了公式简短，先提取出来
        
        # 用 np.array 手写《结构力学》书上的 6x6 经典单元刚度矩阵
        # 注意 Python 里的乘方是用两个星号 ** 表示的，比如 L 的 3 次方是 L**3
        return np.array([
            [ EA/L,        0,           0, -EA/L,        0,           0],
            [     0, 12*EI/L**3,  6*EI/L**2,     0,-12*EI/L**3,  6*EI/L**2],
            [     0,  6*EI/L**2,  4*EI/L,     0, -6*EI/L**2,  2*EI/L],
            [-EA/L,        0,           0,  EA/L,        0,           0],
            [     0,-12*EI/L**3, -6*EI/L**2,     0, 12*EI/L**3, -6*EI/L**2],
            [     0,  6*EI/L**2,  2*EI/L,     0, -6*EI/L**2,  4*EI/L]
        ])

    # 定义一个方法，生成 6x6 的【坐标转换矩阵】 (T矩阵)
    # 它的作用是把倾斜的杆件拉直，或者把局部的力转到全局
    def get_T(self):
        c, s = self.c, self.s
        return np.array([
            [ c,  s,  0,  0,  0,  0], 
            [-s,  c,  0,  0,  0,  0], 
            [ 0,  0,  1,  0,  0,  0],
            [ 0,  0,  0,  c,  s,  0], 
            [ 0,  0,  0, -s,  c,  0], 
            [ 0,  0,  0,  0,  0,  1]
        ])

    # 定义一个方法，生成【全局坐标系】下的刚度矩阵 (k_glob)
    def get_k_glob(self):
        # 矩阵位移法的核心数学公式： K_glob = T转置 * k_loc * T
        # 在 Python numpy 中， 矩阵乘法用 @ 符号表示； .T 表示把矩阵转置 (行变列)
        return self.get_T().T @ self.get_k_loc() @ self.get_T()