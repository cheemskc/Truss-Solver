# 🏗️ Matrix Structural Solver Pro

<div align="center">

![Language](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Framework](https://img.shields.io/badge/GUI-Streamlit-FF4B4B?logo=streamlit)
![Algorithm](https://img.shields.io/badge/Algorithm-Direct%20Stiffness%20Method-purple)
![Mechanics](https://img.shields.io/badge/Physics-Structural%20Mechanics-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A lightweight, interactive Matrix Structural Analysis solver built with Python. 
Designed with an "Engineer's Single-Page Dashboard" philosophy.

专为结构工程与力学研究打造的二维杆系结构求解引擎——拒绝反人类的双击表格，回归极客般流畅的数据阵列录入。

[Design Philosophy](#-设计哲学-design-philosophy) • [Scientific Core](#-核心算法-scientific-core) • [Metrics Explained](#-物理指标解读-metrics-explained) • [Installation](#-快速开始-quick-start)

</div>

---

## 💡 设计哲学 (Design Philosophy)

> 传统的前处理软件总是强迫工程师在无数的弹窗和标签页中迷失，而 Matrix Structural Solver Pro 承认一个事实：**结构力学的本质，就是极其规整的数据矩阵**。

既然如此，就不该用割裂的表单去填补它。本软件的核心使命，是将繁琐的“前处理-求解-后处理”整合进一个极致宽阔的 **单屏工作台 (Single-Page Dashboard)**。通过纯键盘 `Tab` 键即可完成行云流水般的全局参数遍历，按下求解的瞬间，位移与内力报告即刻在同屏呈现。

---

## 🖥️ 界面概览 (Interface Overview)

软件界面采用 "Matrix-Vis Split" (左阵列-右视觉) 的黄金分割布局，专为高效率科研工作流设计。

### 1️⃣ 全局矩阵视图 (Data Matrix Panel)
* **Color-Coded Headers**: 采用顶级表头色彩分组，精准区分 📍 坐标、🔒 约束、🎯 荷载等物理轨道。
* **Smooth Entry**: 彻底摒弃双击编辑，独立组件构成的矩阵表格支持丝滑的连续输入。

### 2️⃣ 可视化引擎 (Visualization Engine)
* **Real-time Rendering**: 坐标录入的瞬间，右侧画布同步绘制几何拓扑、节点编号 (N) 与单元编号 (E)。
* **High-Contrast Canvas**: 强制采用工程蓝图级别的纯白底板与高对比度网格，可直接导出用于论文。

### 3️⃣ 一镜到底后处理 (Seamless Post-Processing)
* **Dashboards**: 提取全局 $|Ux_{max}|, |Uy_{max}|, |M_{max}|$ 作为核心指标高亮显示。
* **MultiIndex Tables**: 利用多重索引技术，将单元的 $i$ 端与 $j$ 端内力自动进行视觉合并，高度对齐学术报告格式。

---

## 🔬 核心算法 (Scientific Core)

超越简单的唯象演示，本工具底层搭载了严谨的 **直接刚度法计算引擎 (Direct Stiffness Engine)**，严格遵循有限元 (FEM) 分析的标准数学协议。

### 1. 单元局部刚度 (Local Stiffness)
针对二维梁/杆单元，基于截面抗拉刚度 $EA$ 与抗弯刚度 $EI$，建立 $6 \times 6$ 局部坐标系刚度矩阵 $[k^e]$。

### 2. 坐标系转换 (Coordinate Transformation)
构建方向余弦矩阵 $[T]$，实现从局部到全局坐标系的物理量映射：
$$[K^e] = [T]^T [k^e] [T]$$

### 3. 系统平衡方程 (System Equilibrium)
将单元全局刚度矩阵 $[K^e]$ 组装为结构总刚度矩阵 $[K]$，结合等效节点荷载向量 $\{P\}$，采用对角线乘大数法处理边界条件，求解核心线性代数方程组：
$$[K] \{U\} = \{P\}$$

### 4. 固端力叠加 (Fixed-End Forces Superposition)
通过节点位移提取局部变形，结合用户输入的初始固端力 $\{f_{FEF}\}$ 计算真实内力：
$$\{f\} = [k^e] [T] \{u\} + \{f_{FEF}\}$$

---

## 📊 物理指标解读 (Metrics Explained)

### 📍 Nodal Displacements (节点位移)

| Column | Symbol | Definition & Significance |
| :--- | :---: | :--- |
| Ux | $U_x$ | **水平位移**。全局坐标系下沿 X 轴的平移，向右为正。 |
| Uy | $U_y$ | **竖向位移**。全局坐标系下沿 Y 轴的平移，向上为正。 |
| $\theta$z | $\theta_z$ | **截面转角**。节点绕 Z 轴的转动角度，逆时针为正 (rad)。 |

### 🔪 Local Elements Forces (单元局部内力)

| Column | Symbol | Definition & Significance |
| :--- | :---: | :--- |
| N | $N$ | **轴力 (Axial Force)**。沿杆件轴线方向，通常规定受拉为正 (+)。 |
| V | $V$ | **剪力 (Shear Force)**。垂直于杆件轴线方向，使微元体顺时针转动为正 (+)。 |
| M | $M$ | **弯矩 (Bending Moment)**。截面上的力矩，通常规定使杆件下部受拉为正 (+)。 |

*(注：本求解器运算为无量纲纯数值计算，推荐外部统一使用国际标准单位制，如 $kN$ 与 $m$)*

---

## ⚠️ 建模边界与避坑指南 (Caveats & Gotchas)

1. **奇异矩阵预警 (Singular Matrix)**
   若点击求解后报错 `求解失败` 或位移达到 $10^{10}$ 数量级，说明系统存在**刚体位移**。请仔细检查是否漏勾选了支座约束，或体系本身为几何可变机构。
2. **极度悬殊的刚度比**
   若强行将极大的 $EA$ (如 $10^{16}$) 与极小的 $EI$ (如 $10^{-5}$) 混用，会引发刚度矩阵病态，导致浮点数截断误差，使得剪力与弯矩结果失真。

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备 (Requirements)
建议在虚拟环境中进行安装：
```bash
pip install streamlit pandas plotly scipy numpy
````

### 2\. 启动引擎 (Launch Engine)

克隆本项目后，在项目根目录的终端中执行：

```bash
streamlit run gui.py
```

-----

## 🖊️ 引用 (Citation)

如果您在学术课程、论文作业或工程验证中使用了本工具，欢迎引用本项目：

> Azeedel. (2026). *Matrix Structural Solver Pro: A lightweight Single-Page Dashboard for 2D frame structural analysis*. [Software]. GitHub. Available at: https://www.google.com/url?sa=E\&source=gmail\&q=https://github.com/您的用户名/Matrix-Structural-Solver

```bibtex
@software{Matrix_Structural_Solver,
  author = {Azeedel},
  title = {Matrix Structural Solver Pro: A lightweight Single-Page Dashboard for 2D frame structural analysis},
  year = {2026},
  publisher = {GitHub},
  url = {[https://github.com/您的用户名/Matrix-Structural-Solver](https://github.com/您的用户名/Matrix-Structural-Solver)}
}
```

```

***

这份 README 将你这几天打磨出的“单屏无双击录入”的 UI 特色，以及严谨的矩阵力学内核完美融合在了一起。你觉得这个排版和文案风格是否达到了你心目中“别人家仓库”的标准？
```
