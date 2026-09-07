# 交接说明：给接手这个项目的下一个 agent

最后更新：2026-09-07。这份文件是给接手 PMaster 项目的下一个 agent（不管是云端还是本地）看的，目的是让它不用重新问用户一遍"这是什么项目/现在进度到哪了"。

## 这是什么项目

PMaster：一个开源的产品经理知识体系，两部分组成：
1. **Claude Skill**（`skill/` 目录）：`pmaster` 技能，`SKILL.md` + `references/` 下 23 篇方法论文件，给 Claude 用的
2. **网页版**（`page/index.html`）：单文件 Web App，把 skill 里的内容 + `page/docs/` 下几篇学习材料渲染成一个可浏览的知识库网站，通过 GitHub Pages 发布

仓库：`github.com/haichangcharles/PMaster`，主分支 `main`。

## 同步方式（重要）

用户的电脑上克隆了这个仓库，路径在 `~/Downloads/PMaster`。云端 Claude session 的 `git push` 会被 Cowork 的 git 凭证代理拦截（"access denied by the git proxy... not in this session's authorized repository set"），这是 Cowork 产品层面的会话仓库授权限制，云端自己解不开，每个新云端 session 都会遇到。

**如果当前 session 已经通过 remote-devices 工具链接了用户的电脑**（工具列表里能看到 `mcp__remote-devices__*`），直接走这条路，不用再折腾 bundle 文件：
1. 云端把改动做完、commit 好
2. `git bundle create /tmp/xxx.bundle <上一次已知同步点>..<当前分支>`
3. `SendUserFile` 把 bundle 发出去拿到 `file_uuid`
4. `mcp__remote-devices__device_commit_files` 把这个 bundle 直接写到用户电脑上的某个路径（比如 `~/Downloads/pmaster-sync.bundle`）
5. `mcp__remote-devices__device_bash` 直接在 `~/mnt/Downloads/PMaster`（注意：device_bash 里看到的路径是 `$HOME/mnt/<连接的文件夹名>/...`，不是 `~/Downloads/...`）跑：
   ```
   cd "$HOME/mnt/Downloads/PMaster"
   git pull ~/mnt/Downloads/pmaster-sync.bundle main
   git push
   ```
   全程不需要用户手动下载/复制粘贴任何东西。

**如果没有链接设备**（`mcp__remote-devices__*` 工具不在列表里），退回旧办法：`git bundle create` 生成包 → `SendUserFile` 发给用户 → 用户在自己电脑上手动 `git pull <bundle> main && git push`。给用户的指令一定要给"复制粘贴就能跑"的完整命令，出错时优先怀疑文件名（浏览器重复下载会自动加后缀，比如 `xxx.bundle` 变成 `xxx_2.bundle`）。

**每次开始工作前**，先确认 GitHub 上（或用户本地）实际停在哪个提交，不要凭这份文档里写的提交号假设——这份文档会过期，`git log` 不会骗人：
```
cd "$HOME/mnt/Downloads/PMaster"  # 或云端重新 clone https://github.com/haichangcharles/PMaster.git
git log --oneline -10
git status
```

## 内容更新的硬规则：一次改动 = 三端同步（最容易翻车的地方）

用户明确要求过：**新内容不能只进 skill 知识库，前端网页里也必须有**。这个仓库有三份"同一内容的不同载体"，改任何一篇 md 之后必须全部走完，缺一个用户就会看到不一致：

1. **源文件**：`skill/references/*.md`（知识库/面试专区）或 `page/docs/*.md`（学习材料，教材体例：是什么/怎么用/用错的样子/面试怎么考）
2. **技能包**：`bash skill/build.sh` 重新打包 `skill/pmaster.skill`
3. **网页**：`python3 page/build_data.py` 把新内容重新嵌进 `page/index.html`（网页读的是内嵌的 `DATA` 常量，不会自动跟着 md 走）
4. **验证**：Playwright 打开 `page/index.html` → `goTab('read')` → `openDoc(key, findNav(key))` → 检查新章节文字正常分段、`<li>` 数量正常、console 无 `pageerror`

**判断该进哪一端**：方法论/判断力 → `skill/references/` 对应主题文件；系统教材式讲解 → `page/docs/handbook.md` 对应章节。**重要的内容两边都要有**（skill 版讲透判断，handbook 版按四段体例讲成教材），不是二选一。

**改章节编号时**：本库大量使用"详见 xxx.md 第 N 节"这种跨文件引用。插入新章节导致后续编号顺延时，必须 `grep -rn "<文件名>.md 第" --include="*.md" .` 把所有引用一起改掉，还有 `handbook.md` 末尾的"触发线索 → 章节号"索引表和 `SKILL.md` 的知识库导航表。

**新增整篇文档时**才需要额外手动改 `page/index.html` 里的三处计数文案（开机动画 `DOCUMENTS ... N OK` / `<h2>N篇文档</h2>` / `CARD_META` 里的领域数）——只改已有文件内容不用动。

## 对外措辞约定（2026-09 用户明确要求，别改回去）

用户会把这个网页和仓库分享给面试官等外部读者，所以**对外可见的措辞一律用"教学/训练/演练"，不用"面试"**：
首页标题、hero 文案、AI 教练页、侧边栏分组名、README 首段、SKILL.md 导航表的行标题，都已按这个约定改过
（分组名是"表达与演练"，四篇文档叫实战题库 / 题型与答题结构 / 追问式教练 / 经历梳理）。

**实现方式很重要**：md 源文件里"面试"等词**原样保留**（skill 要靠它工作），网页版是在
`page/build_data.py` 的 `WEB_WORDING` 表里做**渲染时替换**（面试官→评估者、模拟面试→模拟演练、
面试怎么考→怎么被考察……）。所以写新内容时不用刻意避讳用词，正常写；只有当新词组替换后读着别扭时，
往 `WEB_WORDING` 里补一条固定词组（长词必须排在短词前面，否则会替换出叠词）。改完跑一遍脚本，
再 grep 一次 `page/index.html` 确认没有漏网词。

**这不是要藏内容**——面试相关的方法本身照常写、照常留在文件正文里，改的只是门面定位：
这是一套 PM 知识体系与教学系统，应试只是它的一个应用面。新增内容时沿用这套措辞，
`SKILL.md` frontmatter 的 `description` 里保留"面试/mock interview"关键词是**功能需要**（技能靠它触发），不要删。

## 关键文件/工具

- `skill/build.sh`：把 `skill/SKILL.md` + `skill/references/` 打包成 `skill/pmaster.skill`（顶层目录名必须是 `pmaster`）
- `page/build_data.py`：把 `skill/references/*.md` + `page/docs/*.md` 重新渲染成 HTML，写回 `page/index.html` 里内嵌的 `DATA`/`ORDER` 两个 JS 常量。**改完任何一篇 md 文件之后必须重新跑这个脚本**（`python3 page/build_data.py`，需要 `pip install markdown --break-system-packages`），网页不会自动更新。脚本文件头部写了完整用法，包括新增文档到网页的步骤，以及一个重要的 Python-Markdown 坑：**列表前必须有空行，否则整段渲染成一坨文字**（2026-08 全站修过一次这个 bug，写新内容时留意别复发）
- 改完 `page/index.html` 之后，用 Playwright 截图验证（`goTab('read')` → `openDoc(key, findNav(key))` → 截图 → 检查 console 无 `pageerror`），不要凭感觉相信改对了

## 目前的状态（截至这次更新）

`main` 分支最新提交包含：老王专栏、全站列表排版修复、第 3.5 节 Agent 评测题、`page/build_data.py` 检入仓库、面试题库若干新增、面试"产品 sense"三要素（逻辑/优先级/概括）+ 方案分层表达 + 经历完整性六段自查、以及战略章节新增的 Playing to Win 五问瀑布与 Biddle 的 GLEe/DHM/GEM/SMT 流水线（`strategy.md` 第 2 节 + `handbook.md` 7.2，章节编号已全库顺延对齐）。**别凭这段话假设提交号，跑 `git log --oneline -5` 确认。**

## 还没做完、用户提过但还悬着的事

1. **"网页知识库读起来不像教材，像 AI 写的"**——用户最重的一条反馈，之前只用新加的 `lao-wang.md`（老王产品课笔记专栏）做过一次"好声音应该是什么样"的示范，**没有**对现有 20 多个技能文件做逐篇的声音/例子密度改写。接手时如果要处理这条，先问用户具体是哪几篇让他有这个感觉，别自己瞎猜全部重写。
2. 老王专栏（`skill/references/lao-wang.md`）目前只有用户提供的这一份课堂笔记；如果之后有新的课堂笔记/片段，需要继续扩充这篇文件（文件末尾"说明"那段写好了这个预期）。

## 用户的工作习惯（观察到的，供参考）

- 中文交流，偏好简洁直接的回复，不喜欢过度追问，倾向于"直接做完给我看"而不是反复确认
- 对"读起来像 AI 写的"这类声音/质感问题很敏感，且是目前为止最重的一条意见
- 不太熟悉 git 命令行操作；如果 session 能链接到他的电脑，优先用 remote-devices 工具直接操作，别再让他手动下载 bundle
- 会把小红书/公众号上看到的产品经理相关内容截图发过来，要求"整合/内化进去"——这类零散但有实操价值的内容，判断该放进哪个已有文件（不是每次都要建新文件），参考本次会话的做法：先读目标文件现有结构，找准最贴合的小节插入，别生硬地另起一节
