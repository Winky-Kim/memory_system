# 内存管理模拟器

一个功能完整的内存管理系统模拟器，实现了多种内存分配算法、虚拟内存管理、内存泄漏检测和垃圾回收机制。

## 功能特性

### 1. 动态内存分配算法
- **首次适应算法（First Fit）**：选择第一个足够大的空闲块
- **最佳适应算法（Best Fit）**：选择最小的足够大的空闲块
- **最坏适应算法（Worst Fit）**：选择最大的空闲块
- **下次适应算法（Next Fit）**：从上次分配位置继续查找

### 2. 虚拟内存管理
- 页面管理和地址转换
- 多种页面置换算法：
  - FIFO（先进先出）
  - LRU（最近最少使用）
  - LFU（最少使用频率）
  - Clock（时钟算法）

### 3. 内存泄漏检测
- 自动跟踪内存分配和释放
- 检测未释放的内存块
- 生成详细的泄漏报告

### 4. 内存池管理
- 预分配内存池减少分配开销
- 快速分配和回收
- 支持不同大小的内存块

### 5. 垃圾回收机制
- 标记-清除（Mark-Sweep）算法
- 引用计数
- 分代回收支持

## 项目结构

```
memory_system/
├── src/
│   ├── allocator.py          # 动态内存分配算法
│   ├── virtual_memory.py     # 虚拟内存管理
│   ├── leak_detector.py      # 内存泄漏检测
│   ├── memory_pool.py        # 内存池管理
│   ├── garbage_collector.py  # 垃圾回收机制
│   └── utils.py              # 工具函数
├── tests/
│   ├── test_allocator.py
│   ├── test_virtual_memory.py
│   ├── test_leak_detector.py
│   ├── test_memory_pool.py
│   └── test_garbage_collector.py
├── main.py                   # 主程序
├── requirements.txt          # 依赖包
└── README.md
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 运行主程序
```bash
python main.py
```

### 运行测试
```bash
python -m pytest tests/
```

## 示例

### 1. 内存分配
```python
from src.allocator import MemoryAllocator

allocator = MemoryAllocator(total_size=1024, algorithm='first_fit')
ptr1 = allocator.allocate(100)
ptr2 = allocator.allocate(200)
allocator.free(ptr1)
allocator.display_memory()
```

### 2. 虚拟内存管理
```python
from src.virtual_memory import VirtualMemoryManager

vm = VirtualMemoryManager(page_size=4096, num_frames=10, algorithm='lru')
vm.access_page(5)
vm.access_page(3)
vm.display_status()
```

### 3. 内存泄漏检测
```python
from src.leak_detector import MemoryLeakDetector

detector = MemoryLeakDetector()
ptr = detector.allocate(256)
# 忘记释放内存
report = detector.check_leaks()
print(report)
```

### 4. 内存池
```python
from src.memory_pool import MemoryPool

pool = MemoryPool(block_size=64, num_blocks=100)
obj1 = pool.allocate()
obj2 = pool.allocate()
pool.free(obj1)
pool.display_stats()
```

### 5. 垃圾回收
```python
from src.garbage_collector import GarbageCollector

gc = GarbageCollector()
obj1 = gc.create_object(size=100)
obj2 = gc.create_object(size=200)
gc.add_reference(obj1, obj2)
gc.collect()
gc.display_stats()
```

## 性能指标

模拟器会跟踪和显示以下性能指标：
- 内存碎片率
- 分配成功率
- 页面置换次数
- 垃圾回收耗时
- 内存利用率

## 许可证

MIT License
