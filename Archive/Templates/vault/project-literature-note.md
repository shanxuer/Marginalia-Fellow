---
type: literature
status: active
created: YYYY-MM-DD
citekey:
tags: []
---

# {{title}}

## Citation

Full citation, DOI, URL, or Zotero citekey.

> [!info] Zotero
> Citekey: [@{{citekey}}]
> Bibliography: {{bibliography}}

## 一句话价值

{% persist "one-line-value" %}
这篇论文对当前项目最有用的地方是什么？
{% endpersist %}

## 核心贡献

{% persist "core-contribution" %}
- 
{% endpersist %}

## 可借用内容

{% persist "transferable-parts" %}
- 概念：
- 方法：
- 表达：
{% endpersist %}

## 对项目的启发

{% persist "project-implications" %}
- 支持：
- 挑战：
- 可转化：
{% endpersist %}

## Annotations

{% persist "annotations" %}
{% for annotation in annotations %}
{% if annotation.annotatedText %}

> [!quote] Page {{annotation.page}}
> {{annotation.annotatedText}}

{% endif %}
{% if annotation.comment %}
**Comment:** {{annotation.comment}}
{% endif %}
{% if annotation.imageRelativePath %}
![[{{annotation.imageRelativePath}}]]
{% endif %}

{% endfor %}
{% endpersist %}
