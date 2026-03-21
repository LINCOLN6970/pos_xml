# POS XML 处理流程

从 main 入口出发，按实际调用顺序列出各模块的执行链路。

---

## 一、完整流程

```
1. main.py（入口）
      │
      ▼
2. process_file()
      │
      ├─ open(input_file, "rb").read()  →  content (bytes)
      │
      ▼
3. utils/xslt_processor.apply(content)
      │     · etree.parse(BytesIO(content)) 解析 XML
      │     · XSLT 变换 (Normalize001.xsl)
      │     · 返回 root (lxml Element)
      │
      ▼
4. choose_extractor(input_file)  →  TransactionExtractor 或 ShiftSummaryExtractor
      │
      ▼
5. extractor.extract(root)
      │     · extractors/base_extractor.py（BaseExtractor）
      │     · 内部使用 utils/xml_loader.ns（命名空间）
      │
      ▼
6. TransactionExtractor._process_extraction(root)
      │     · extract_single_transaction(sale_event, root)
      │     · 遍历 TransactionLine 子节点
      │
      ▼
7. line_extractors（通过 get_line_extractors()）
      │     · FuelLineExtractor, ItemLineExtractor, TenderLineExtractor, FuelPrepayLineExtractor
      │     · 这些模块内部使用 utils/xml_loader.ns
      │
      ▼
8. utils/file_writer.write_json(result, output_file)
```

---

## 二、顺序总结（按调用链）

| 顺序 | 模块/文件 | 作用 |
|------|-----------|------|
| 1 | **main.py** | 入口，读取文件，调用 process_file |
| 2 | **utils/xslt_processor** | 解析 bytes、执行 XSLT，输出 root |
| 3 | **extractors**（TransactionExtractor / ShiftSummaryExtractor） | 大 extractor，提取整棵 root |
| 4 | **line_extractors** | 行级提取（fuel、item、tender、fuel_prepay） |
| 5 | **utils/file_writer** | 写入 JSON 文件 |

---

## 三、关于 xml_loader

- **`utils/xml_loader.load_xml()` 未参与主流程**：main 从不调用它。
- 主流程只用 **`utils/xml_loader.ns`**（命名空间字典），供 extractors 和 line_extractors 在 `find`、`findall` 时使用。
- 正确顺序为：**main → xslt_processor → extractors → line_extractors → file_writer**；xml_loader 只做依赖，不是流程中的独立步骤。
