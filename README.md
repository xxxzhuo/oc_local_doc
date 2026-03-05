# OC Local Doc - OpenClaw 本地文档仓库

**最强大脑 AI 公司** 的官方文档和数据存储仓库。

---

## 📁 目录结构

```
oc_local_doc/
├── projects/           # 项目文档
│   ├── digikey-crawler/
│   ├── ai-company/
│   └── ...
├── skills/             # 技能文件
├── configs/            # 配置文件
├── logs/               # 执行日志
├── datasheets/         # 爬取的规格书等数据
├── memory/             # 记忆备份
└── README.md           # 仓库说明
```

---

## 🎯 用途

### 1. 项目文档
存储所有项目的完整文档，包括：
- 需求分析
- 技术方案
- 执行报告
- 测试结果

### 2. 技能文件
存储为 OpenClaw 开发的技能：
- SKILL.md 文件
- 相关脚本和工具
- 配置示例

### 3. 配置文件
存储重要配置：
- OpenClaw 配置备份
- 环境变量示例
- 工具配置文件

### 4. 执行日志
记录 AI 公司任务执行日志：
- 任务执行报告
- 错误日志
- 性能指标

### 5. 数据文件
存储爬取和生成的数据：
- 规格书 PDF
- 数据集
- 导出文件

### 6. 记忆备份
定期备份 OpenClaw 记忆：
- MEMORY.md
- 日常记忆文件
- 重要决策记录

---

## 🚀 使用方式

### 克隆仓库

```bash
git clone git@github.com:xxxzhuo/oc_local_doc.git
cd oc_local_doc
```

### 添加新文档

```bash
# 添加到对应目录
cp my-document.md projects/my-project/

# 提交
git add .
git commit -m "feat: 添加 xxx 文档"
git push
```

### 定期备份

建议每天备份重要数据：
```bash
# 备份 MEMORY.md
cp ~/.openclaw/workspace/MEMORY.md memory/

# 备份项目文档
cp -r ~/.openclaw/workspace/oc_doc/* projects/
```

---

## 📋 命名规范

### 文件命名
- 使用小写字母
- 单词间用 `-` 连接
- 包含日期时使用 `YYYY-MM-DD` 格式

**示例：**
- `digikey-crawler-report.md`
- `2026-03-05-task-report.md`

### 提交信息规范

```
feat: 新功能
fix: Bug 修复
docs: 文档更新
style: 格式调整
refactor: 重构
test: 测试
chore: 构建/工具
```

**示例：**
```bash
git commit -m "feat: 添加 DigiKey 爬虫执行报告"
git commit -m "docs: 更新 AI 公司组织架构文档"
```

---

## 🔐 安全提醒

### ❌ 不要提交

- [ ] API Key 和 Secret
- [ ] 密码和凭证
- [ ] 个人隐私信息
- [ ] 敏感配置文件

### ✅ 应该提交

- [ ] 公开文档
- [ ] 技术方案
- [ ] 执行报告
- [ ] 配置文件模板（不含敏感信息）

---

## 📊 统计

| 项目 | 数量 | 最后更新 |
|------|------|----------|
| 项目文档 | - | - |
| 技能文件 | - | - |
| 配置文件 | - | - |
| 执行日志 | - | - |
| 数据文件 | - | - |

---

## 👥 团队

**最强大脑 AI 公司**

- 🧠 AI 中枢 (最强大脑)
- 📋 产品经理
- 💻 前端工程师
- ⚙️ 后端工程师
- 🧪 测试工程师
- 🚀 运维工程师

---

## 📝 更新日志

### 2026-03-05
- ✅ 仓库初始化
- ✅ 创建目录结构
- ✅ 添加 README 和 .gitignore

---

_最后更新：2026-03-05_
_版本：v1.0_
