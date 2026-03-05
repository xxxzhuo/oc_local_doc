# 🤖 AI 公司 - 最强大脑技能包

## 概述

这个技能包为 AI 公司的每个角色提供专属 AI 助手能力。

---

## 角色技能

### 1️⃣ 产品经理 AI 助手

**技能文件：** `skills/pm-assistant/SKILL.md`

**能力：**
- 需求分析与整理
- PRD 自动生成
- 竞品分析
- 用户调研
- 数据洞察

**使用示例：**
```
用户："帮我分析这个用户反馈，生成 PRD"
AI：分析反馈 → 提取需求 → 生成 PRD 初稿 → 输出验收标准
```

---

### 2️⃣ 前端 AI 助手

**技能文件：** `skills/fe-assistant/SKILL.md`

**能力：**
- UI 代码生成
- 组件库推荐
- 性能优化建议
- 跨平台适配
- 可访问性检查

**使用示例：**
```
用户："创建一个用户列表组件，支持搜索和分页"
AI：生成 React 组件 → 添加 TypeScript 类型 → 实现搜索分页 → 添加单元测试
```

---

### 3️⃣ 后端 AI 助手

**技能文件：** `skills/be-assistant/SKILL.md`

**能力：**
- API 设计
- 数据库建模
- 业务逻辑实现
- 性能优化
- 安全检查

**使用示例：**
```
用户："设计一个用户管理系统，包含登录注册"
AI：设计数据库 schema → 生成 API 接口 → 实现认证逻辑 → 添加单元测试
```

---

### 4️⃣ 测试 AI 助手

**技能文件：** `skills/qa-assistant/SKILL.md`

**能力：**
- 测试用例生成
- 自动化脚本编写
- 测试执行
- Bug 分析
- 质量报告

**使用示例：**
```
用户："为这个登录功能生成测试用例"
AI：分析功能 → 生成边界测试 → 生成异常测试 → 输出测试脚本
```

---

### 5️⃣ 运维 AI 助手

**技能文件：** `skills/ops-assistant/SKILL.md`

**能力：**
- 部署自动化
- 监控配置
- 故障诊断
- 日志分析
- 容量规划

**使用示例：**
```
用户："API 响应变慢了，帮我分析原因"
AI：检查监控 → 分析日志 → 定位瓶颈 → 给出优化建议
```

---

## 协作技能

### 项目启动

```bash
# 创建新项目
ai-project-init --name "新项目" --team "pm,fe,be,qa,ops"

# 自动生成:
# - 项目结构
# - 技术栈配置
# - CI/CD 流水线
# - 监控配置
```

### 迭代管理

```bash
# 创建迭代
ai-sprint-create --duration "2 周" --goals "目标列表"

# 每日站会
ai-standup --team "all" --time "10:00"

# 迭代总结
ai-sprint-review --sprint "S01"
```

### 代码协作

```bash
# 代码审查
ai-code-review --pr 123 --reviewers "fe,be"

# 合并检查
ai-merge-check --branch "feature/xxx" --target "develop"

# 冲突解决
ai-resolve-conflicts --pr 123
```

---

## 自动化脚本

### 每日任务

```bash
#!/bin/bash
# daily-check.sh

# 系统健康检查
ai-health-check

# 代码质量检查
ai-quality-check

# 测试覆盖率检查
ai-coverage-check

# 生成日报
ai-daily-report --output "daily-$(date +%Y%m%d).md"
```

### 发布流程

```bash
#!/bin/bash
# release.sh

VERSION=$1

# 版本检查
ai-version-check --version $VERSION

# 自动化测试
ai-run-tests --suite "all"

# 构建
ai-build --version $VERSION

# 部署
ai-deploy --env production --version $VERSION --strategy canary

# 验证
ai-verify-deploy --version $VERSION

# 通知
ai-notify --channel "dingtalk" --message "发布完成 $VERSION"
```

---

## 监控告警

### 指标监控

```yaml
# monitoring-config.yaml
metrics:
  - name: api_latency
    threshold: 200ms
    alert: P1
    
  - name: error_rate
    threshold: 0.1%
    alert: P0
    
  - name: cpu_usage
    threshold: 80%
    alert: P2
    
  - name: memory_usage
    threshold: 85%
    alert: P2
```

### 告警规则

```bash
# 告警配置
ai-alert-config --metric "api_latency" --threshold "200ms" --channel "dingtalk"

# 告警测试
ai-alert-test --rule "api_latency"
```

---

## 知识库

### 文档自动生成

```bash
# API 文档
ai-docs-api --input "src/api/" --output "docs/api/"

# 技术文档
ai-docs-tech --input "src/" --output "docs/tech/"

# 用户手册
ai-docs-user --input "docs/features/" --output "docs/manual/"
```

### 知识检索

```bash
# 搜索文档
ai-search --query "如何部署" --scope "docs/"

# 问答
ai-ask --question "CI/CD 流程是什么"

# 总结
ai-summarize --docs "project-docs/" --length "short"
```

---

## 团队成长

### 技能评估

```bash
# 个人技能评估
ai-skill-assess --person "张三" --role "fe"

# 团队技能图谱
ai-team-skills --team "all"

# 培训建议
ai-training-plan --gaps "技能差距"
```

### 技术分享

```bash
# 分享主题推荐
ai-topic-suggest --trend "frontend"

# 分享材料生成
ai-presentation --topic "React 18 新特性" --duration "30min"

# 问答整理
ai-qa-summary --session "分享会 2026-03-05"
```

---

## 配置示例

### 团队配置

```json
{
  "team": {
    "name": "AI 产品研发团队",
    "members": [
      {"name": "张三", "role": "pm", "skills": ["需求分析", "数据分析"]},
      {"name": "李四", "role": "fe", "skills": ["React", "TypeScript"]},
      {"name": "王五", "role": "be", "skills": ["Node.js", "MySQL"]},
      {"name": "赵六", "role": "qa", "skills": ["自动化测试", "性能测试"]},
      {"name": "钱七", "role": "ops", "skills": ["K8s", "AWS"]}
    ],
    "aiAssistants": {
      "enabled": true,
      "roles": ["pm", "fe", "be", "qa", "ops"]
    }
  }
}
```

### AI 助手配置

```json
{
  "ai": {
    "model": "qwen3.5-plus",
    "capabilities": {
      "codeGeneration": true,
      "codeReview": true,
      "testGeneration": true,
      "docGeneration": true,
      "logAnalysis": true,
      "monitoring": true
    },
    "integrations": {
      "github": true,
      "dingtalk": true,
      "jira": true,
      "grafana": true
    }
  }
}
```

---

## 快速开始

### 1. 安装技能包

```bash
cd /Users/mac/.openclaw/workspace/oc_doc
# 技能包已创建
```

### 2. 配置团队

```bash
# 编辑 team-config.json
# 添加团队成员和角色
```

### 3. 启用 AI 助手

```bash
# 在 openclaw.json 中启用 AI 助手
# 配置各角色助手
```

### 4. 开始使用

```bash
# 产品经理
ai-pm --task "生成 PRD" --input "需求.md"

# 前端
ai-fe --task "生成组件" --spec "组件需求.md"

# 后端
ai-be --task "生成 API" --spec "API 设计.md"

# 测试
ai-qa --task "生成测试" --input "功能.md"

# 运维
ai-ops --task "部署" --version "v1.0"
```

---

_版本：v1.0_
_创建日期：2026-03-05_
_作者：最强大脑 AI 公司_
