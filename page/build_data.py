#!/usr/bin/env python3
"""
把 skill/references/*.md 和 page/docs/*.md 重新渲染成 HTML，写回 page/index.html
里内嵌的 `const DATA = {...}` 和 `const ORDER = {...}` 两个 JS 常量。

用法：
    cd PMaster
    python3 page/build_data.py
    # 需要 python3 -m pip install markdown --break-system-packages（如果没装过）

改完任何一篇 skill/references/*.md 或 page/docs/*.md 之后，网页版不会自动更新——
必须重新跑这个脚本，把新内容重新嵌进 page/index.html，再截图/预览确认。

注意本脚本会对网页版做一层**对外措辞替换**（见下方 WEB_WORDING）：skill 源文件里保留
"面试"等词，渲染进网页时统一换成"评估/演练/考察"。写新内容时不用刻意避讳，
但新出现的词组如果替换后读着别扭，往 WEB_WORDING 里补一条固定词组即可。

新增一篇文档到网页的步骤：
    1. 文件放进 skill/references/<key>.md（知识库/表达与演练）或 page/docs/<key>.md（学习材料）
    2. 在下面的 TITLES 字典里加一行 "<key>": "<侧边栏显示的短标题>"
    3. 如果是 page/docs 里的文件，在 PAGE_DOCS 字典里加一行 "<key>": "page/docs/<文件名>.md"
    4. 在下面的 ORDER 字典里，把 "<key>" 加进对应分组（学习材料 / 知识库 / 表达与演练）的数组里
    5. 跑本脚本
    6. 手动更新 page/index.html 里的三处计数（脚本不自动改，因为它们是自然语言文案）：
       - `'DOCUMENTS ........ N OK'`（开机动画行数）
       - `<h2>N篇文档，一张地图。</h2>`（首页大标题，中文数字）
       - `CARD_META['知识库']` 或 `CARD_META['学习材料']` 里的"N 个领域"文案
    7. 用 Playwright 截图验证（goTab('read') → openDoc(key, findNav(key)) → 截图 →
       检查 console 无 pageerror）

【踩过的坑，别再踩】Python-Markdown 有个反直觉规则：一段说明文字后面紧跟一个列表
（`- item` 或 `1. item`），中间如果没有空行，Python-Markdown 不会把它识别成列表，
会整段坍缩成一个 <p> 段落，"- "变成字面量文本混在句子里，网页上看起来就是一大坨
不分行的文字。写新内容时，列表前后必须有空行，两个方向都要注意：
    正确：
        说明文字：

        - 列表项一
        - 列表项二

    错误（会渲染成一坨）：
        说明文字：
        - 列表项一
        - 列表项二
本仓库 2026-08 做过一次全量修复（commit "fix: pervasive markdown list-rendering
bug"），但这是个容易复发的模式，新写内容时留意。
"""
import re
import json
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("需要先安装 markdown 库：python3 -m pip install markdown --break-system-packages")

REPO = Path(__file__).resolve().parent.parent

TITLES = {
    'handbook': '框架与模板手册',
    'scenario20': '一个场景×20框架',
    'answers': '自问自答模板集',
    'agent-eval-qa': 'Agent 评测·自问自答',
    'pm-thinking-os': '思维方式：链路与归因',
    'industry-sense': '行业语感：案例与数字',
    'lao-wang': '老王专栏：产品课笔记',
    'discovery': '产品发现与用户研究',
    'strategy': '产品战略与定位',
    'strategy-advanced': '高阶战略',
    'business-analysis': '商业分析',
    'prioritization': '优先级与路线图',
    'execution': 'PRD 与执行',
    'metrics': '指标与实验',
    'data-system': '数据体系与看板',
    'data-selection': '数据选型地图',
    'metric-library': '指标库全集（27 域）',
    'growth': '增长与变现',
    'ai-products': 'AI 产品',
    'ai-evals': '模型与 Agent 评估',
    'stakeholders-career': '干系人与成长',
    'china-playbook': '国内实战打法',
    'frameworks': '经典框架速查',
    'question-bank': '实战题库',
    'pm-job-interview-prep': '题型与答题结构',
    'interview-coach': '追问式教练',
    'experience-mining': '经历梳理',
}

PAGE_DOCS = {
    'handbook': 'page/docs/handbook.md',
    'scenario20': 'page/docs/one-scenario-20-frameworks.md',
    'answers': 'page/docs/model-answers.md',
    'agent-eval-qa': 'page/docs/agent-eval-qa.md',
}

ORDER = {
    '学习材料': ["handbook", "scenario20", "answers", "agent-eval-qa"],
    '知识库': ["pm-thinking-os", "industry-sense", "lao-wang", "discovery", "strategy", "strategy-advanced",
             "business-analysis", "prioritization", "execution", "metrics", "data-system", "data-selection",
             "metric-library", "growth", "ai-products", "ai-evals", "stakeholders-career", "china-playbook",
             "frameworks"],
    '表达与演练': ["question-bank", "pm-job-interview-prep", "interview-coach", "experience-mining"],
}


# ---------------------------------------------------------------------------
# 网页版对外措辞替换表（只作用于 page/index.html，不改 skill 源文件）
#
# 用户明确要求：skill 里保留"面试"等措辞（技能要靠它工作），但**网页对外不出现**——
# 网页的定位是"PM 知识体系与教学系统"，应试只是它的一个应用面。
# 所以这里做一层展示层替换：md 源文件原样不动，只在渲染进网页时换词。
#
# 不替换"求职"：它绝大多数出现在 one-scenario-20-frameworks.md 里——那篇的案例产品本身
# 就是一个简历/求职工具，是正经的产品分析素材，换掉会把案例讲坏。
#
# 改动注意：这是有序列表，长词组必须排在短词前面（"模拟面试官"要先于"面试官"先于"面试"），
# 否则会替换出叠词。改完跑一次本脚本，再 grep 一遍 page/index.html 确认没有漏网词。
WEB_WORDING = [
    # —— 必须保留原意的专有说法（最先处理，避免被下面的通用规则改错）——
    ("投递→面试转化率", "投递→约面转化率"),          # 招聘产品的真实指标名，"约面"是同义行话
    ("面试市场营销候选人", "评估市场营销候选人"),      # 老王招人的真实经历，不是应试语境
    # —— 固定词组 ——
    ("产品经理岗位的求职面试", "产品经理岗位的能力评估"),   # 否则会出现"岗位的岗位评估"叠词
    ("被面试官看成同行", "被资深评估者看成同行"),            # "被评估者"单用有歧义
    ("面什么岗位、什么公司类型、什么时间面？", "目标是什么岗位、什么公司类型、什么时间？"),
    ("准备 PM 面试的求职者", "想系统补齐方法论的人"),
    ("面试怎么考", "怎么被考察"),
    ("面试怎么用", "演练时怎么用"),
    ("简历与面试语言", "简历与自述语言"),
    ("思考与面试", "思考与评估应对"),
    ("面试和汇报", "评估场合和汇报"),
    ("面试讲产品案例", "讲产品案例"),
    ("体系类面试题", "体系类演练题"),
    ("面试估算题", "估算演练题"),
    ("面试答行为题", "答行为题"),
    ("刚面完真实面试", "刚走完一轮真实评估"),
    ("用户面完真实面试", "用户走完一轮真实评估"),
    ("真实面试复盘", "真实评估复盘"),
    ("之前面过吗", "之前经历过吗"),
    ("跨行业面试", "跨行业评估"),
    ("英文面试", "英文演练"),
    ("海外面试", "海外评估"),
    ("外企面试体系", "外企评估体系"),
    ("公开面经与题集", "公开资料与题集"),
    ("应试辅导", "备考式辅导"),
    ("应试包装", "表达包装"),
    # —— 通用词，从长到短 ——
    ("模拟面试官", "模拟评估者"),
    ("真实面试官", "资深评估者"),
    ("面试官", "评估者"),
    ("模拟面试", "模拟演练"),
    ("真实面试", "真实评估场景"),
    ("求职面试", "岗位评估"),
    ("面试错题", "错题"),
    ("面试题", "演练题"),
    ("面试前", "演练前"),
    ("面试中", "演练中"),
    ("面经", "公开资料"),
    ("面试", "评估"),
]


def to_web_wording(text):
    """把 md 源文本换成网页对外措辞。只在网页渲染路径上调用。"""
    for old, new in WEB_WORDING:
        text = text.replace(old, new)
    return text


def source_path(key):
    if key in PAGE_DOCS:
        return REPO / PAGE_DOCS[key]
    return REPO / "skill" / "references" / f"{key}.md"


def build():
    content = {}
    for group, keys in ORDER.items():
        for key in keys:
            path = source_path(key)
            text = to_web_wording(path.read_text(encoding="utf-8"))
            html = markdown.markdown(text, extensions=["tables", "fenced_code"])
            content[key] = {"title": TITLES[key], "html": html}

    data_json = json.dumps({"content": content}, ensure_ascii=False)
    data_json_safe = data_json.replace("</", "<\\/")  # safe to embed inside <script>

    index_path = REPO / "page" / "index.html"
    page = index_path.read_text(encoding="utf-8")

    new_page, n = re.subn(
        r'const DATA = \{.*?\};\n(?=const ORDER)',
        lambda m: 'const DATA = ' + data_json_safe + ';\n',
        page, count=1, flags=re.S,
    )
    assert n == 1, f"DATA replace count={n}, check page/index.html still has the expected marker"
    page = new_page

    order_lines = ["const ORDER = {"]
    for i, (g, keys) in enumerate(ORDER.items()):
        keys_str = ", ".join(f'"{k}"' for k in keys)
        comma = "," if i < len(ORDER) - 1 else ""
        order_lines.append(f" '{g}':[{keys_str}]{comma}")
    order_lines.append("};")
    order_js = "\n".join(order_lines)

    new_page, n = re.subn(r'const ORDER = \{.*?\n\};', lambda m: order_js, page, count=1, flags=re.S)
    assert n == 1, f"ORDER replace count={n}, check page/index.html still has the expected marker"
    page = new_page

    index_path.write_text(page, encoding="utf-8")
    print(f"DATA + ORDER updated in page/index.html. Doc count: {len(content)}")
    print("别忘了手动更新: 开机动画 DOCUMENTS 行数 / <h2>N篇文档</h2> / CARD_META 里的领域数文案。")


if __name__ == "__main__":
    build()
