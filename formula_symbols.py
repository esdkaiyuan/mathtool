from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import Iterable


@dataclass(frozen=True)
class LatexSymbol:
    label: str
    snippet: str
    hint: str = ""
    group: str = ""

    @property
    def display(self) -> str:
        return self.label


@dataclass(frozen=True)
class LatexSymbolGroup:
    name: str
    symbols: tuple[LatexSymbol, ...]


SYMBOL_GROUPS: tuple[LatexSymbolGroup, ...] = (
    LatexSymbolGroup(
        "基础",
        (
            LatexSymbol("a⁄b", r"\frac{a}{b}", "分式：分子 a，分母 b"),
            LatexSymbol("x²", r"x^{2}", "上标：把 2 改为指数"),
            LatexSymbol("xᵢ", r"x_{i}", "下标：把 i 改为下标"),
            LatexSymbol("xᵢ²", r"x_{i}^{2}", "上下标：同时带下标和指数"),
            LatexSymbol("√x", r"\sqrt{x}", "平方根：根号内为 x"),
            LatexSymbol("ⁿ√x", r"\sqrt[n]{x}", "n 次根：根指数 n，被开方数 x"),
            LatexSymbol("|x|", r"\left| x \right|", "绝对值"),
            LatexSymbol("‖x‖", r"\left\| x \right\|", "范数"),
            LatexSymbol("(x)", r"\left( x \right)", "自适应圆括号"),
            LatexSymbol("[x]", r"\left[ x \right]", "自适应方括号"),
            LatexSymbol("{x}", r"\left\{ x \right\}", "自适应花括号"),
            LatexSymbol("⟨x⟩", r"\left\langle x \right\rangle", "尖括号"),
        ),
    ),
    LatexSymbolGroup(
        "运算",
        (
            LatexSymbol("±", r"\pm "),
            LatexSymbol("∓", r"\mp "),
            LatexSymbol("×", r"\times "),
            LatexSymbol("÷", r"\div "),
            LatexSymbol("⋅", r"\cdot "),
            LatexSymbol("∗", r"\ast "),
            LatexSymbol("∘", r"\circ "),
            LatexSymbol("⊕", r"\oplus "),
            LatexSymbol("⊗", r"\otimes "),
            LatexSymbol("∧", r"\wedge "),
            LatexSymbol("∨", r"\vee "),
            LatexSymbol("¬", r"\neg "),
        ),
    ),
    LatexSymbolGroup(
        "关系",
        (
            LatexSymbol("=", r"= "),
            LatexSymbol("≠", r"\ne "),
            LatexSymbol("≈", r"\approx "),
            LatexSymbol("≡", r"\equiv "),
            LatexSymbol("<", r"< "),
            LatexSymbol(">", r"> "),
            LatexSymbol("≤", r"\le "),
            LatexSymbol("≥", r"\ge "),
            LatexSymbol("≪", r"\ll "),
            LatexSymbol("≫", r"\gg "),
            LatexSymbol("∝", r"\propto "),
            LatexSymbol("∼", r"\sim "),
            LatexSymbol("⊂", r"\subset "),
            LatexSymbol("⊃", r"\supset "),
            LatexSymbol("⊆", r"\subseteq "),
            LatexSymbol("⊇", r"\supseteq "),
        ),
    ),
    LatexSymbolGroup(
        "微积分",
        (
            LatexSymbol("∫", r"\int f(x)\,dx", "不定积分：被积函数 f(x)，微分 dx"),
            LatexSymbol("∫ₐᵇ", r"\int_{a}^{b} f(x)\,dx", "定积分：下限 a，上限 b"),
            LatexSymbol("∬", r"\iint_{D} f(x,y)\,dA", "二重积分：区域 D"),
            LatexSymbol("∭", r"\iiint_{\Omega} f(x,y,z)\,dV", "三重积分：区域 Omega"),
            LatexSymbol("∮", r"\oint_{C} f(z)\,dz", "闭合曲线积分：路径 C"),
            LatexSymbol("∂", r"\partial "),
            LatexSymbol("∂f⁄∂x", r"\frac{\partial f}{\partial x}", "偏导：函数 f，对 x 求偏导"),
            LatexSymbol("df⁄dx", r"\frac{d f}{d x}", "导数：函数 f，对 x 求导"),
            LatexSymbol("limₓ→ₐ", r"\lim_{x \to a} f(x)", "极限：x 趋近 a"),
            LatexSymbol("∞", r"\infty "),
            LatexSymbol("∇", r"\nabla "),
            LatexSymbol("∆", r"\Delta "),
        ),
    ),
    LatexSymbolGroup(
        "大型",
        (
            LatexSymbol("Σ", r"\sum_{i=1}^{n} a_i", "求和：i 从 1 到 n"),
            LatexSymbol("Π", r"\prod_{i=1}^{n} a_i", "连乘：i 从 1 到 n"),
            LatexSymbol("⋃", r"\bigcup_{i=1}^{n} A_i", "并集"),
            LatexSymbol("⋂", r"\bigcap_{i=1}^{n} A_i", "交集"),
            LatexSymbol("∪", r"\cup "),
            LatexSymbol("∩", r"\cap "),
            LatexSymbol("∈", r"\in "),
            LatexSymbol("∉", r"\notin "),
            LatexSymbol("∀", r"\forall "),
            LatexSymbol("∃", r"\exists "),
            LatexSymbol("∅", r"\emptyset "),
            LatexSymbol("ℕ", r"\mathbb{N} "),
            LatexSymbol("ℤ", r"\mathbb{Z} "),
            LatexSymbol("ℚ", r"\mathbb{Q} "),
            LatexSymbol("ℝ", r"\mathbb{R} "),
            LatexSymbol("ℂ", r"\mathbb{C} "),
        ),
    ),
    LatexSymbolGroup(
        "希腊",
        (
            LatexSymbol("α", r"\alpha "),
            LatexSymbol("β", r"\beta "),
            LatexSymbol("γ", r"\gamma "),
            LatexSymbol("δ", r"\delta "),
            LatexSymbol("ε", r"\epsilon "),
            LatexSymbol("ζ", r"\zeta "),
            LatexSymbol("η", r"\eta "),
            LatexSymbol("θ", r"\theta "),
            LatexSymbol("ι", r"\iota "),
            LatexSymbol("κ", r"\kappa "),
            LatexSymbol("λ", r"\lambda "),
            LatexSymbol("μ", r"\mu "),
            LatexSymbol("ν", r"\nu "),
            LatexSymbol("ξ", r"\xi "),
            LatexSymbol("π", r"\pi "),
            LatexSymbol("ρ", r"\rho "),
            LatexSymbol("σ", r"\sigma "),
            LatexSymbol("τ", r"\tau "),
            LatexSymbol("φ", r"\phi "),
            LatexSymbol("χ", r"\chi "),
            LatexSymbol("ψ", r"\psi "),
            LatexSymbol("ω", r"\omega "),
            LatexSymbol("Γ", r"\Gamma "),
            LatexSymbol("Λ", r"\Lambda "),
            LatexSymbol("Ω", r"\Omega "),
        ),
    ),
    LatexSymbolGroup(
        "箭头",
        (
            LatexSymbol("→", r"\to "),
            LatexSymbol("←", r"\leftarrow "),
            LatexSymbol("↔", r"\leftrightarrow "),
            LatexSymbol("⇒", r"\Rightarrow "),
            LatexSymbol("⇐", r"\Leftarrow "),
            LatexSymbol("⇔", r"\Leftrightarrow "),
            LatexSymbol("↦", r"\mapsto "),
            LatexSymbol("↑", r"\uparrow "),
            LatexSymbol("↓", r"\downarrow "),
            LatexSymbol("↗", r"\nearrow "),
            LatexSymbol("↘", r"\searrow "),
            LatexSymbol("⇢", r"\rightharpoonup "),
        ),
    ),
    LatexSymbolGroup(
        "结构",
        (
            LatexSymbol("x̄", r"\bar{x}", "横线：变量 x"),
            LatexSymbol("x̂", r"\hat{x}", "帽子：变量 x"),
            LatexSymbol("x̃", r"\tilde{x}", "波浪：变量 x"),
            LatexSymbol("x⃗", r"\vec{x}", "向量：变量 x"),
            LatexSymbol("x˙", r"\dot{x}", "一阶导点"),
            LatexSymbol("x¨", r"\ddot{x}", "二阶导点"),
            LatexSymbol("▦", r"\substack{a\quad b \\ c\quad d}", "堆叠矩阵：第一行为 a b，第二行为 c d"),
            LatexSymbol("(▦)", r"\left( \substack{a\quad b \\ c\quad d} \right)", "圆括号矩阵"),
            LatexSymbol("[▦]", r"\left[ \substack{a\quad b \\ c\quad d} \right]", "方括号矩阵"),
            LatexSymbol("{x¦y", r"\left\{ \substack{x,\quad x>0 \\ -x,\quad x\leq 0} \right.", "分段函数"),
            LatexSymbol("sin x", r"\sin x"),
            LatexSymbol("cos x", r"\cos x"),
            LatexSymbol("tan x", r"\tan x"),
            LatexSymbol("ln x", r"\ln x"),
            LatexSymbol("logₐx", r"\log_{a} x", "以 a 为底的对数"),
            LatexSymbol("eˣ", r"e^{x}"),
        ),
    ),
)


def iter_symbols() -> Iterable[LatexSymbol]:
    return (
        LatexSymbol(symbol.label, symbol.snippet, symbol.hint, group.name)
        for group in SYMBOL_GROUPS
        for symbol in group.symbols
    )


def find_symbol(label: str) -> LatexSymbol:
    for symbol in iter_symbols():
        if symbol.label == label:
            return symbol
    raise KeyError(label)


def preferred_cursor_offset(snippet: str) -> int:
    first_empty_group = snippet.find("{}")
    if first_empty_group >= 0:
        return first_empty_group + 1

    for marker in ("{a}", "{x}", "{f}", "{i=1}", "{D}", "{\\Omega}"):
        index = snippet.find(marker)
        if index >= 0:
            return index + 1

    double_space = snippet.find("  ")
    if double_space >= 0:
        return double_space + 1
    return len(snippet)
