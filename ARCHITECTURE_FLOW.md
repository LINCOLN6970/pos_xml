# pos_xml_qilong 项目架构与数据流

## 一、GPT 描述核对

| GPT 说法 | 实际情况 |
|----------|----------|
| 「从 Blob 获取 bytes 后，传入 xml_loader 或 xslt_processor」 | **不准确**：main 只传 bytes 给 `xslt_processor`，**不**使用 `xml_loader.load_xml`。 |
| 「main 调用大 extractor，大 extractor 再调用 line extractor」 | **正确**。 |
| 「base extractor 和 register 是行级提取的基础」 | **部分正确**：`BaseExtractor` 是大 extractor 的基类；`registry` 和 `@register` 当前**未使用**。 |

## 二、重要更正

1. **xml_loader**：`load_xml(file_path)` 未参与主流程。主流程只用 `xml_loader` 的 `ns`（命名空间字典）。
2. **registry**：`extractors/registry.py` 的 `register`、`get_extractors` 当前未被 main 或任何 extractor 调用。
3. **bytes 来源**：目前是本地文件 `open(..., "rb")`；若接 Azure Blob，只需把 `content = blob_client.download_blob().readall()` 之类替换读文件那一步，后续流程不变。

---

## 三、实际数据流（树状图）

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  入口：main.py                                                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  main()                                                                         │
│    └── process_file(input_file, output_file=None)                               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  1.  bytes 获取（当前：本地文件；未来：Azure Blob 同理）                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  content = open(input_file, "rb").read()   →   bytes                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  2.  bytes → 标准化 XML root（不经过 xml_loader.load_xml）                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  utils/xslt_processor.py                                                        │
│    apply(content: bytes)                                                        │
│      ├── etree.parse(BytesIO(content)) → XML 树                                 │
│      ├── XSLT 变换 (xslt/Normalize001.xsl)                                      │
│      └── return tree.getroot()   →   root (lxml Element)                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  3.  选择大 extractor（硬编码，未用 registry）                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  choose_extractor(input_file)                                                   │
│    ├── is_shift_summary? → ShiftSummaryExtractor(source_file)                    │
│    └── else → TransactionExtractor(source_file)                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  4.  大 extractor 提取（继承 BaseExtractor）                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  extractors/base_extractor.py  BaseExtractor                                     │
│    extract(root) → _process_extraction(root) + 元数据                            │
│    get_text(node, xpath, ns)  ← 使用 utils/xml_loader.ns                         │
│                                                                                 │
│  ├── TransactionExtractor.extract(root)                                        │
│  │     _process_extraction → extract_single_transaction(sale_event, root)       │
│  │                                                                              │
│  └── ShiftSummaryExtractor.extract(root)                                       │
│        _process_extraction → 遍历 SaleEvent → extract_single_transaction(...)   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  5.  extract_single_transaction（内部 _TransactionExtractorLogic）                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  extractors/transaction_extractor.py                                            │
│    └── _TransactionExtractorLogic._extract(sale_event, root)                    │
│          ├── 取 header：JournalHeader, TransmissionHeader, TransactionSummary   │
│          ├── deal_lines: _extract_deal_lines(...)                                │
│          └── 遍历 TransactionDetailGroup / TransactionLine 子节点               │
│                for child in tx_line:                                             │
│                  localname = tag_localname(child)  ← line_extractors.base         │
│                  if localname == "FuelLine"    → fuel_extractor.extract_fuel_line │
│                  elif localname == "ItemLine" → item_extractor.extract_item_line │
│                  elif localname == "TenderInfo"→ tender_extractor.extract_tender  │
│                  elif localname == "FuelPrepayLine" → _extract_fuel_prepay_line   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  6.  line extractors（按 localname 硬编码分发，未用 @register）                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  line_extractors/base.py     tag_localname, get_text, get_attr  ← 使用 xml_loader.ns │
│  line_extractors/fuel_extractor.py     extract_fuel_line(child, tx_id, seq_num) │
│  line_extractors/item_extractor.py     extract_item_line(...)                   │
│  line_extractors/tender_extractor.py   extract_tender_line(...)                  │
│  transaction_extractor._extract_fuel_prepay_line  (内联)                         │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│  7.  输出 JSON                                                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│  utils/file_writer.write_json(result, output_file)                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 四、模块依赖关系（简化）

```
main.py
  ├── utils.file_writer (write_json)
  ├── utils.xslt_processor (apply)
  ├── extractors.transaction_extractor (TransactionExtractor)
  └── extractors.shift_summary_extractor (ShiftSummaryExtractor)

extractors/transaction_extractor.py
  ├── extractors.base_extractor (BaseExtractor, get_text)
  ├── line_extractors.base (tag_localname)
  ├── line_extractors.fuel_extractor
  ├── line_extractors.item_extractor
  ├── line_extractors.tender_extractor
  └── utils.xml_loader (ns)

extractors/shift_summary_extractor.py
  ├── extractors.base_extractor (BaseExtractor, get_text)
  ├── extractors.transaction_extractor (extract_single_transaction)
  └── utils.xml_loader (ns)

utils/xml_loader.py
  └── 仅 ns 被使用；load_xml 未参与主流程

extractors/registry.py
  └── 当前未被任何模块调用
```

---

## 五、Azure bytes 接入点

若从 Azure Blob 获取 bytes，只需在 `process_file` 中替换：

```python
# 当前：本地文件
content = open(input_file, "rb").read()

# 未来：Azure Blob
# content = blob_client.download_blob().readall()
```

其余流程不变：`content` → `xslt_processor.apply(content)` → `root` → `extractor.extract(root)`。
