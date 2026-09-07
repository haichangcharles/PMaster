# PMaster

一个面向 Claude 的产品经理知识库 Skill：让 AI 以头部梯队 PM 的判断标准工作——覆盖需求分析、产品战略、PRD、数据指标、增长变现、AI 产品、商业分析，以及一套完整的教学与演练系统。

A comprehensive Product Management knowledge-base skill for Claude: top-tier PM judgment across discovery, strategy, execution, metrics, growth, AI products, and business analysis — plus a full PM job-interview coaching system (mock interviewer, experience mining, question bank).

## 目录结构 / Repo layout

```
skill/                      Claude Skill
  SKILL.md                  入口：角色、决策原则、按任务路由
  references/               17 篇领域文档
  examples/                 真实输出示例
  build.sh                  重新打包 → pmaster.skill
  pmaster.skill            打包产物，可直接安装

page/                       网页版（GitHub Pages 自动发布）
  index.html                单文件站点：文档阅读 + AI 教练 + 3D 首页
  docs/                     学习材料（手册 / 场景精讲 / 模板集）
  assets-src/               3D 场景与渲染脚本源码
```

## 安装 Skill / Install

**Claude.ai / Cowork**：下载 [`skill/pmaster.skill`](skill/pmaster.skill)，在 Settings → Capabilities → Skills 上传。

**Claude Code**：把 `skill/` 下的 `SKILL.md` 与 `references/` 放到 `~/.claude/skills/pmaster/`。

改完内容重新打包：`./skill/build.sh`

Skill 的 17 个领域文件（[`skill/references/`](skill/references)）覆盖：产品发现、战略、高阶战略、商业分析、优先级、PRD 与执行、指标与实验、数据体系、增长变现、AI 产品、干系人与成长、国内打法、经典框架速查，以及演练四件套（题库 / 题型与答题结构 / 教练规则 / 经历梳理）。

## 网页版 / Web

`page/index.html` 是一个**单文件网站**（零依赖、无 CDN）：全部文档在线阅读、可折叠目录、深色主题，首页是一台可拖拽旋转的 3D 复古电脑（three.js 已内联打包），另带一个用你自己 API Key 运行的 AI 产品教练。双击即可本地打开。

仓库已配置 GitHub Actions 自动发布 `page/` 到 Pages——在 **Settings → Pages → Source** 选 **GitHub Actions** 即可，之后每次改动 `page/` 会自动上线。

## 配套学习材料 / Learning materials

`page/docs/` 目录下是三份写给人（而不是 AI）的学习材料，与 skill 构成完整学习体系：

1. **[handbook.md](page/docs/handbook.md)**《产品经理框架与模板使用手册》——30+ 框架的系统教材，每个框架含"是什么/怎么用/用错的样子/怎么被考察"，附按触发线索排列的全书索引。**建议从这本开始通读建立地图。**
2. **[one-scenario-20-frameworks.md](page/docs/one-scenario-20-frameworks.md)**《一个场景 × 20 个框架》——用同一个案例（AI 简历工具的留存危机）演示 20 个框架如何协同工作，含迁移练习。
3. **[model-answers.md](page/docs/model-answers.md)**《自问自答模板集》——五大题型的 90 秒模板答案 + 逐句解析 + 框架卡片。

`skill/examples/` 目录是本 skill 的真实输出示例（需求评估+PRD、模拟演练开场、商业分析），供安装前预览效果。

## 适用人群

在职 PM（日常决策与文档质量提升）、正在系统准备 PM 岗位的候选人（校招/社招/海外/转岗）、以及想系统学习产品方法论的 junior。

## License

MIT
