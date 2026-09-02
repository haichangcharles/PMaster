# 交接说明：给接手这个项目的下一个 agent

最后更新：2026-09-02。这份文件是给接手 PMaster 项目的下一个 agent（不管是云端还是本地）看的，目的是让它不用重新问用户一遍"这是什么项目/现在进度到哪了"。

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

## 关键文件/工具

- `skill/build.sh`：把 `skill/SKILL.md` + `skill/references/` 打包成 `skill/pmaster.skill`（顶层目录名必须是 `pmaster`）
- `page/build_data.py`：把 `skill/references/*.md` + `page/docs/*.md` 重新渲染成 HTML，写回 `page/index.html` 里内嵌的 `DATA`/`ORDER` 两个 JS 常量。**改完任何一篇 md 文件之后必须重新跑这个脚本**（`python3 page/build_data.py`，需要 `pip install markdown --break-system-packages`），网页不会自动更新。脚本文件头部写了完整用法，包括新增文档到网页的步骤，以及一个重要的 Python-Markdown 坑：**列表前必须有空行，否则整段渲染成一坨文字**（2026-08 全站修过一次这个 bug，写新内容时留意别复发）
- 改完 `page/index.html` 之后，用 Playwright 截图验证（`goTab('read')` → `openDoc(key, findNav(key))` → 截图 → 检查 console 无 `pageerror`），不要凭感觉相信改对了

## 目前的状态（截至这次更新）

`main` 分支已经是最新，GitHub 和用户本地都同步到了这份文档写下时的最新提交（`老王专栏` + 全站列表排版修复 + 第 3.5 节 Agent 评测题 + `page/build_data.py` 检入仓库 + 面试题库若干新增内容）。跑 `git log --oneline -5` 确认。

## 还没做完、用户提过但还悬着的事

1. **"网页知识库读起来不像教材，像 AI 写的"**——用户最重的一条反馈，之前只用新加的 `lao-wang.md`（老王产品课笔记专栏）做过一次"好声音应该是什么样"的示范，**没有**对现有 20 多个技能文件做逐篇的声音/例子密度改写。接手时如果要处理这条，先问用户具体是哪几篇让他有这个感觉，别自己瞎猜全部重写。
2. 老王专栏（`skill/references/lao-wang.md`）目前只有用户提供的这一份课堂笔记；如果之后有新的课堂笔记/片段，需要继续扩充这篇文件（文件末尾"说明"那段写好了这个预期）。

## 用户的工作习惯（观察到的，供参考）

- 中文交流，偏好简洁直接的回复，不喜欢过度追问，倾向于"直接做完给我看"而不是反复确认
- 对"读起来像 AI 写的"这类声音/质感问题很敏感，且是目前为止最重的一条意见
- 不太熟悉 git 命令行操作；如果 session 能链接到他的电脑，优先用 remote-devices 工具直接操作，别再让他手动下载 bundle
- 会把小红书/公众号上看到的产品经理相关内容截图发过来，要求"整合/内化进去"——这类零散但有实操价值的内容，判断该放进哪个已有文件（不是每次都要建新文件），参考本次会话的做法：先读目标文件现有结构，找准最贴合的小节插入，别生硬地另起一节
