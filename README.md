# Matrix Structural Solver Pro

<div align="center">

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Open%20App-FF4B4B?style=for-the-badge&logo=streamlit)](https://truss-solver-8knkhfmdm2ggmv546hp7yt.streamlit.app/)

![Language](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Framework](https://img.shields.io/badge/GUI-Streamlit-FF4B4B?logo=streamlit)
![Algorithm](https://img.shields.io/badge/Algorithm-Matrix%20Displacement%20Method-purple)
![Mechanics](https://img.shields.io/badge/Physics-Structural%20Mechanics-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

专为结构工程与力学研究打造的二维杆系结构矩阵位移法求解引擎。

[快速开始 (Quick Start)](#-快速开始-quick-start) • [计算原理 (Principles)](#-计算原理-calculation-principles) • [避坑指南 (Caveats)](#-计算建模注意事项-calculation-caveats) • [本地部署 (Local)](#-本地部署-local-deployment)

</div>

---

## 🚀 快速开始 (Quick Start)

本项目已部署至云端，无需任何本地配置，推荐直接在浏览器中访问体验：

👉 **[点击进入 Matrix Structural Solver 在线版](https://truss-solver-8knkhfmdm2ggmv546hp7yt.streamlit.app/)**

---

## 📐 计算原理 (Calculation Principles)

本项目核心算法基于经典的**矩阵位移法 (Matrix Displacement Method)**：

1. **局部刚度矩阵建立**: 
   对于每一个二维梁/杆单元，根据其材料弹性模量 $E$、截面面积 $A$、截面惯性矩 $I$ 以及单元长度 $L$，建立 $6 \times 6$ 的局部坐标系单元刚度矩阵 $[k^e]$。
2. **坐标变换**: 
   计算单元从局部坐标系到全局坐标系的转换矩阵 $[T]$，得到全局坐标系下的单元刚度矩阵：
   $$[K^e] = [T]^T [k^e] [T]$$
3. **全局刚度矩阵组装**: 
   根据单元与节点的拓扑连接关系（自由度映射），将所有单元的全局刚度矩阵 $[K^e]$ 叠加，组装成总结构刚度矩阵 $[K]$。
4. **荷载向量组装**: 
   将输入的节点荷载与单元的等效节点荷载，合并生成结构的综合节点总载向量 $\{P\}$。
5. **引入边界条件**: 
   采用对角线乘大数法 (Penalty Method) 或划零置一法处理支座约束，修正 $[K]$ 和 $\{P\}$。
6. **求解位移与内力**: 
   求解线性代数方程组：
   $$[K] \{U\} = \{P\}$$
   解出所有节点的全局位移 $\{U\}$。随后提取各单元的节点位移，通过 $[T]$ 转换回局部坐标系，并结合初始固端力计算出单元的最终局部内力。

---

## ⚠️ 计算建模注意事项 (Calculation Caveats)

### 局部坐标系与正负号约定 (Sign Conventions)
* **全局坐标系**: $X$ 轴水平向右为正，$Y$ 轴竖直向上为正，力矩与转角均以**逆时针**方向为正。
* **局部坐标系**: 单元的局部 $x$ 轴始终**从起点 (Node i) 指向终点 (Node j)**。局部 $y$ 轴由局部 $x$ 轴逆时针旋转 $90^\circ$ 得到。
* **内力正负号**: 输出的内力结果严格遵循单元局部坐标系。

---

## 💻 本地部署 (Local Deployment)

如果您需要修改底层代码或进行二次开发，可以按照以下步骤在本地运行：

### 1. 环境准备 (Requirements)
```bash
pip install streamlit pandas plotly scipy numpy
