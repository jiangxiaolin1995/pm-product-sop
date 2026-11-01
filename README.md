# 产品经理 SOP · pm-product-sop

把一个产品需求从当前阶段持续推进：先复用已有资料和决定，再选择快速、标准或探索流程，在需要时调用付费权益路径分析与交互原型 Skill，并维护同一份需求推进记录。

## 阅读与交付

- [完整离线 HTML](assets/产品经理SOP.html)：下载原始文件后直接打开，包含 SOP 全文、八步导航、五组调用指令和需求模板。支持复制、下载模板及打印，无需联网或运行服务。
- [SOP 来源文档](references/sop.md)：每一步的输入、动作、Skill、产出、完成标准、参与者和异常处理。
- [需求推进模板](assets/requirement-template.md)：一个需求从开始到复盘持续使用的记录。

## 安装

将此仓库放进 Codex 的 Skills 目录。使用默认个人目录时：

```sh
git clone https://github.com/jiangxiaolin1995/pm-product-sop.git "$HOME/.codex/skills/pm-product-sop"
```

两个专项 Skill 按需调用；已安装的无需重复安装：

- [pm-payment-journey](https://github.com/jiangxiaolin1995/pm-payment-journey)：付费、余额、权益、解锁和不付费路径分析。
- [pm-prototype-workbench](https://github.com/jiangxiaolin1995/pm-prototype-workbench)：三栏交互原型、需求文字与页面说明。

新环境尚未安装时，可分别克隆到同一 Skills 目录：

```sh
git clone https://github.com/jiangxiaolin1995/pm-payment-journey.git "$HOME/.codex/skills/pm-payment-journey"
git clone https://github.com/jiangxiaolin1995/pm-prototype-workbench.git "$HOME/.codex/skills/pm-prototype-workbench"
```

目标目录已存在时先检查并保留已有改动。自定义 Skills 根目录时替换对应路径。安装后在能够发现新 Skill 的会话中使用。

## 使用

支持自动选择，也可以明确调用：

```text
使用 $pm-product-sop 推进这个产品需求：【需求描述】。
当前资料：【材料或已有推进记录】。
本次希望完成：【具体环节或产出】。
按当前阶段调用合适的 Skill，并维护需求推进记录。
```

后续直接提供需求或继续补充同一需求。Skill 会读取已有记录、确认当前阶段、执行本次范围内的工作，并更新交接摘要、产物、依据与下一步。已确认信息与授权直接沿用，关键业务取舍仍由实际负责人决定。

小范围任务走快速流程；不需要每次都运行两个专项 Skill。原型按提供的规则实现，协助设计业务规则需有对应授权；默认交付可编辑工作 HTML，只读导出按用户要求执行。

如果另有 `pm-master` 总控，可增加一条路由：产品需求的创建、接续和推进记录维护交给 `pm-product-sop`；单独分析、审查等仍按本次范围执行。

## 文件与维护

| 文件 | 用途 |
| --- | --- |
| `SKILL.md` | 自动选择、阶段判断、两个 Skill 的调度与记录维护规则 |
| `agents/openai.yaml` | 显示名称与默认调用提示 |
| `references/sop.md` | SOP 正文的唯一维护来源 |
| `assets/requirement-template.md` | 可复用记录模板 |
| `assets/产品经理SOP.html` | 由来源文档生成的离线交付文件 |
| `scripts/init_requirement.py` | 初始化新记录，拒绝覆盖已有文件 |
| `scripts/build_handbook.py` | 生成内联样式、脚本与模板的单文件 HTML |

日常使用 Skill 和初始化记录只需要 Python 标准库。重新构建 HTML 时使用 Python 3.10 或更新版本，并安装开发依赖：

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/build_handbook.py
python3 -m unittest discover -s tests -v
```

修改正文或模板后重新生成 HTML；修改界面或交互后，还需在真实浏览器检查目录、复制、下载、打印和窄屏阅读。HTML 不保存实际项目进度，项目进度保存在每个需求自己的 Markdown 记录里。

流程能推进到哪里取决于当前任务授权和实际证据。团队评审、用户测试、发布与效果结果按实际发生情况记录。
