## 1. 概述 (Overview)

- 对verdi的cov功能进行patch
- **创建日期:** 2025-10-19
- **当前状态:** 已完成
- **主要负责人:** eda

---

## 2. 目标与范围 (Goals & Scope)

- **范围:** verdi 2023 - verdi 2025

---

## 3. 目录结构说明 (Directory Structure)


---

## 4. 版本与历史 (Version & History)

- 2025-10-19 - v1.0 
  
  支持verdi版本列表：
  
  - 2023.03-SP1
  - 2023.03-SP2
  - 2023.12-SP1
  - 2023.12-SP2
  - 2024.09
  - 2024.09-SP1
  - 2025.06
  
- 2025-10-19 - v1.1

  新增版本检查功能

- 2025-10-19 - v1.2
  
  新增verdi版本：
  
  - 2024.09-SP2
  - 2025.06-SP1

---

## 5. 关键信息与资源 (Key Info & Resources)

- 使用objdump查看汇编代码
  - ` $ objdump -D libucapi.so &> dump `

- 参考资料：https://bbs.eetop.cn/thread-979305-1-1.html

---

## 6. 使用说明与注意事项 (Usage & Notes)
 - 2024后的版本patch后可能会卡死，建议重新lmgrd

