## Email 值对象

### 实现完成
- 文件路径: backend/app/domain/value_objects/email.py
- 特性:
  - 正则验证: 标准邮箱格式
  - 最大长度: 255 字符
  - 自动转小写
  - 去除首尾空格
  - 不可变 dataclass (frozen=True)
  - local_part 和 domain 属性
  - __str__, __eq__, __hash__ 方法

### 验证结果
- 创建: ✅
- 转小写: ✅
- 去空格: ✅
- 相等性: ✅
- 属性访问: ✅
- 验证失败: ✅
- 不可变性: ✅

