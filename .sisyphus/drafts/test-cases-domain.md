# 测试用例清单 - Domain 层单元测试

> **目标**: 覆盖所有 Domain 层核心业务逻辑，确保业务规则独立可测试  
> **目标覆盖率**: 95%  
> **格式**: Given-When-Then  
> **状态说明**: ✅ 已实现 | ⬜ 待实现  
> **当前状态**: 🔴 **严重缺失** - Domain 层目前几乎无单元测试  
> **优先级**: **P0（最高）** - 经 Metis 审核，Domain 层测试是上层测试的基础，应优先实现

---

## 📋 文档导航

- [P0 - Value Objects（安全关键）](#p0---value-objects) - 值对象验证
- [P0 - Aggregates（业务核心）](#p0---aggregates) - 聚合根业务逻辑  
- [P1 - Entities](#p1---entities) - 实体行为
- [P1 - Factories](#p1---factories) - 工厂创建逻辑
- [P2 - Domain Events](#p2---domain-events) - 领域事件（如已实现）
- [P0 - 并发安全测试（新增）](#p0---并发安全测试)

---

## P0 - Value Objects

### 1.1 Slug

**源文件**: `app/domain/value_objects/slug.py`

#### 1.1.1 有效 Slug 创建
```gherkin
⬜ 待实现 - tests/unit/domain/value_objects/test_slug.py

---

## 1. Value Objects

### 1.1 Slug

**源文件**: `app/domain/value_objects/slug.py`

#### 1.1.1 有效 Slug 创建
```gherkin
⬜ 待实现 - tests/unit/domain/value_objects/test_slug.py

Scenario: 使用有效值创建 Slug
  Given 有效 slug 值 "my-test-slug"
  When 创建 Slug("my-test-slug")
  Then 应该成功创建
  And value 应该为 "my-test-slug"

Scenario: 使用带大写字母创建 Slug（自动转小写）
  When 创建 Slug("My-Test-Slug")
  Then value 应该为 "my-test-slug"

Scenario: 使用单字符创建 Slug
  When 创建 Slug("a")
  Then 应该成功

Scenario: 使用纯数字创建 Slug
  When 创建 Slug("123")
  Then 应该成功

Scenario: 使用最大长度创建 Slug
  When 创建 Slug("a" * 128)
  Then 应该成功
```

#### 1.1.2 无效 Slug 验证
```gherkin
⬜ 待实现

Scenario: 使用空字符串创建 Slug
  When 创建 Slug("")
  Then 应该抛出 ValidationError
  And 错误消息应该为 "Slug cannot be empty"

Scenario: 使用空格创建 Slug
  When 创建 Slug("   ")
  Then 应该抛出 ValidationError

Scenario: 使用带下划线的 Slug
  When 创建 Slug("my_test_slug")
  Then 应该抛出 ValidationError
  And 错误消息应该提示只能包含小写字母、数字和连字符

Scenario: 使用带空格的 Slug
  When 创建 Slug("my test slug")
  Then 应该抛出 ValidationError

Scenario: 使用特殊字符创建 Slug
  When 创建 Slug("test@slug!")
  Then 应该抛出 ValidationError

Scenario: 使用连字符开头创建 Slug
  When 创建 Slug("-test-slug")
  Then 应该抛出 ValidationError

Scenario: 使用连字符结尾创建 Slug
  When 创建 Slug("test-slug-")
  Then 应该抛出 ValidationError

Scenario: 使用连续连字符创建 Slug
  When 创建 Slug("test--slug")
  Then 应该抛出 ValidationError

Scenario: 使用超长字符串创建 Slug
  When 创建 Slug("a" * 129)
  Then 应该抛出 ValidationError
  And 错误消息应该提示不能超过 128 字符
```

#### 1.1.3 from_name 工厂方法
```gherkin
⬜ 待实现

Scenario: 从名称生成 Slug
  Given 名称 "My Test Skill"
  When 调用 Slug.from_name("My Test Skill")
  Then 应该返回 Slug("my-test-skill")

Scenario: 从带特殊字符的名称生成 Slug
  When 调用 Slug.from_name("Skill @ Home #1!")
  Then 应该返回 Slug("skill-home-1")

Scenario: 从连续空格的名称生成 Slug
  When 调用 Slug.from_name("My   Skill")
  Then 应该返回 Slug("my-skill")

Scenario: 从带连字符的名称生成 Slug
  When 调用 Slug.from_name("My - Test - Skill")
  Then 应该返回 Slug("my-test-skill")

Scenario: 从空名称生成 Slug
  When 调用 Slug.from_name("")
  Then 应该抛出 ValidationError
  And 错误消息应该为 "Cannot generate slug from empty name"

Scenario: 从仅含特殊字符的名称生成 Slug
  When 调用 Slug.from_name("@#$%")
  Then 应该抛出 ValidationError
```

#### 1.1.4 相等性比较
```gherkin
⬜ 待实现

Scenario: 相同值的 Slug 应该相等
  Given slug1 = Slug("test-slug")
  And slug2 = Slug("test-slug")
  Then slug1 == slug2 应该为 True
  And hash(slug1) == hash(slug2) 应该为 True

Scenario: 不同值的 Slug 应该不相等
  Given slug1 = Slug("test-slug-1")
  And slug2 = Slug("test-slug-2")
  Then slug1 == slug2 应该为 False

Scenario: Slug 与字符串比较
  Given slug = Slug("test-slug")
  Then slug == "test-slug" 应该为 False（类型不同）
```

---

### 1.2 Path

**源文件**: `app/domain/value_objects/path.py`

#### 1.2.1 有效路径创建
```gherkin
⬜ 待实现 - tests/unit/domain/value_objects/test_path.py

Scenario: 创建简单文件路径
  When 创建 Path("file.txt")
  Then value 应该为 "file.txt"
  And is_file() 应该返回 True
  And is_directory() 应该返回 False

Scenario: 创建目录路径
  When 创建 Path("src/")
  Then value 应该为 "src/"
  And is_directory() 应该返回 True
  And is_file() 应该返回 False

Scenario: 创建嵌套路径
  When 创建 Path("src/components/Button.tsx")
  Then value 应该为 "src/components/Button.tsx"

Scenario: 创建空路径
  When 创建 Path("")
  Then value 应该为 ""

Scenario: 使用最大长度创建路径
  When 创建 Path("a" * 512)
  Then 应该成功

Scenario: 路径自动规范化（去除多余斜杠）
  When 创建 Path("src//components///file.txt")
  Then value 应该为 "src/components/file.txt"

Scenario: 路径自动规范化（处理点）
  When 创建 Path("./src/file.txt")
  Then value 应该为 "src/file.txt"
```

#### 1.2.2 无效路径验证
```gherkin
⬜ 待实现

Scenario: 使用绝对路径创建 Path
  When 创建 Path("/etc/passwd")
  Then 应该抛出 ValidationError
  And 错误消息应该提示 "Path must be relative"

Scenario: 使用路径遍历序列创建 Path
  When 创建 Path("../secret.txt")
  Then 应该抛出 ValidationError
  And 错误消息应该提示 "Path contains traversal sequences"

Scenario: 使用复杂遍历序列创建 Path
  When 创建 Path("src/../../../etc/passwd")
  Then 应该抛出 ValidationError

Scenario: 使用波浪号创建 Path
  When 创建 Path("~/.bashrc")
  Then 应该抛出 ValidationError

Scenario: 使用 URL 编码遍历序列创建 Path
  When 创建 Path("%2e%2e%2fsecret.txt")
  Then 应该抛出 ValidationError

Scenario: 使用超长路径创建 Path
  When 创建 Path("a" * 513)
  Then 应该抛出 ValidationError
  And 错误消息应该提示不能超过 512 字符

Scenario: 使用空路径创建 Path（null 字节攻击）
  When 创建 Path("file.txt\x00.sh")
  Then 应该抛出 ValidationError 或正确处理
```

#### 1.2.3 路径操作
```gherkin
⬜ 待实现

Scenario: 获取文件扩展名
  Given path = Path("src/components/Button.tsx")
  Then path.extension() 应该返回 "tsx"
  And path.has_extension() 应该返回 True

Scenario: 获取无扩展名文件
  Given path = Path("Makefile")
  Then path.extension() 应该返回 None
  And path.has_extension() 应该返回 False

Scenario: 获取目录扩展名
  Given path = Path("src/")
  Then path.extension() 应该返回 None

Scenario: 获取文件名
  Given path = Path("src/components/Button.tsx")
  Then path.filename() 应该返回 "Button.tsx"

Scenario: 获取根目录文件名
  Given path = Path("file.txt")
  Then path.filename() 应该返回 "file.txt"

Scenario: 获取父目录
  Given path = Path("src/components/Button.tsx")
  Then path.parent() 应该返回 Path("src/components/")

Scenario: 获取多级父目录
  Given path = Path("src/components/Button.tsx")
  Then path.parent().parent() 应该返回 Path("src/")

Scenario: 连接路径
  Given path = Path("src/")
  When 调用 path.join("components")
  Then 应该返回 Path("src/components")

Scenario: 使用 / 运算符连接路径
  Given path = Path("src/")
  When 调用 path / "components" / "Button.tsx"
  Then 应该返回 Path("src/components/Button.tsx")

Scenario: 空路径的父目录
  Given path = Path("")
  Then path.parent() 应该返回 Path("")
```

#### 1.2.4 相等性比较
```gherkin
⬜ 待实现

Scenario: 相同值的路径应该相等
  Given path1 = Path("src/file.txt")
  And path2 = Path("src/file.txt")
  Then path1 == path2 应该为 True

Scenario: 规范化后相同的路径应该相等
  Given path1 = Path("src//file.txt")
  And path2 = Path("src/file.txt")
  Then path1 == path2 应该为 True
```

---

### 1.3 Email

**源文件**: `app/domain/value_objects/email.py`

#### 1.3.1 有效邮箱创建
```gherkin
⬜ 待实现 - tests/unit/domain/value_objects/test_email.py

Scenario: 创建简单邮箱
  When 创建 Email("test@example.com")
  Then 应该成功
  And value 应该为 "test@example.com"

Scenario: 创建带加号的邮箱
  When 创建 Email("test+tag@example.com")
  Then 应该成功

Scenario: 创建带子域的邮箱
  When 创建 Email("test@mail.example.com")
  Then 应该成功

Scenario: 创建带连字符的邮箱
  When 创建 Email("test-user@example-site.com")
  Then 应该成功

Scenario: 创建大写邮箱（自动转小写）
  When 创建 Email("Test@Example.COM")
  Then value 应该为 "test@example.com"

Scenario: 使用最大长度创建邮箱
  When 创建有效长邮箱（接近 254 字符限制）
  Then 应该成功
```

#### 1.3.2 无效邮箱验证
```gherkin
⬜ 待实现

Scenario: 使用空字符串创建邮箱
  When 创建 Email("")
  Then 应该抛出 ValidationError

Scenario: 使用无效格式创建邮箱
  When 创建 Email("not-an-email")
  Then 应该抛出 ValidationError

Scenario: 使用缺少 @ 的字符串创建邮箱
  When 创建 Email("testexample.com")
  Then 应该抛出 ValidationError

Scenario: 使用缺少域名的邮箱创建
  When 创建 Email("test@")
  Then 应该抛出 ValidationError

Scenario: 使用缺少用户名的邮箱创建
  When 创建 Email("@example.com")
  Then 应该抛出 ValidationError

Scenario: 使用带空格的邮箱创建
  When 创建 Email("test user@example.com")
  Then 应该抛出 ValidationError

Scenario: 使用超长邮箱创建
  When 创建 Email("a" * 250 + "@example.com")
  Then 应该抛出 ValidationError

Scenario: 使用多个 @ 的邮箱创建
  When 创建 Email("test@user@example.com")
  Then 应该抛出 ValidationError

Scenario: 使用无效字符的邮箱创建
  When 创建 Email("test\u003cuser\u003e@example.com")
  Then 应该抛出 ValidationError
```

#### 1.3.3 邮箱解析
```gherkin
⬜ 待实现

Scenario: 获取本地部分（用户名）
  Given email = Email("test+tag@example.com")
  Then email.local_part() 应该返回 "test+tag"

Scenario: 获取域名部分
  Given email = Email("test@mail.example.com")
  Then email.domain() 应该返回 "mail.example.com"
```

---

## P0 - Aggregates

### 2.1 Skill Aggregate

**源文件**: `app/domain/aggregates/skill.py`

#### 2.1.1 Skill 创建
```gherkin
⬜ 待实现 - tests/unit/domain/aggregates/test_skill.py

Scenario: 创建默认 Skill
  When 创建 Skill()
  Then id 应该被自动生成
  And version 应该为 1
  And is_public 应该为 False
  And name 应该为空字符串
  And created_at 和 updated_at 应该被设置

Scenario: 创建带属性的 Skill
  When 创建 Skill(
    user_id=uuid,
    name="Test Skill",
    slug=Slug("test-skill"),
    description="A test skill"
  )
  Then 所有属性应该被正确设置
```

#### 2.1.2 update_name
```gherkin
⬜ 待实现

Scenario: 更新 Skill 名称
  Given skill = Skill(name="Old Name")
  When 调用 skill.update_name("New Name")
  Then skill.name 应该为 "New Name"
  And skill.slug 应该更新为 Slug("new-name")
  And skill.version 应该增加
  And skill.updated_at 应该更新

Scenario: 使用空字符串更新名称
  Given skill = Skill(name="Old Name")
  When 调用 skill.update_name("")
  Then 应该抛出 ValueError

Scenario: 使用仅含空格的字符串更新名称
  Given skill = Skill(name="Old Name")
  When 调用 skill.update_name("   ")
  Then 应该抛出 ValueError

Scenario: 使用前后有空格的名称
  Given skill = Skill(name="Old Name")
  When 调用 skill.update_name("  New Name  ")
  Then skill.name 应该为 "New Name"（自动 trim）
```

#### 2.1.3 update_description
```gherkin
⬜ 待实现

Scenario: 更新描述
  Given skill = Skill(description="Old desc")
  When 调用 skill.update_description("New desc")
  Then skill.description 应该为 "New desc"
  And skill.version 应该增加

Scenario: 清空描述
  Given skill = Skill(description="Old desc")
  When 调用 skill.update_description(None)
  Then skill.description 应该为 None

Scenario: 设置空字符串描述
  Given skill = Skill(description="Old desc")
  When 调用 skill.update_description("")
  Then skill.description 应该为 ""
```

#### 2.1.4 set_public
```gherkin
⬜ 待实现

Scenario: 设置公开
  Given skill = Skill(is_public=False)
  When 调用 skill.set_public(True)
  Then skill.is_public 应该为 True
  And skill.version 应该增加

Scenario: 设置私有
  Given skill = Skill(is_public=True)
  When 调用 skill.set_public(False)
  Then skill.is_public 应该为 False
```

#### 2.1.5 assign_tree
```gherkin
⬜ 待实现

Scenario: 分配 Tree
  Given skill = Skill()
  And tree_id = UUID
  When 调用 skill.assign_tree(tree_id)
  Then skill.tree_id 应该为 tree_id
  And skill.version 应该增加

Scenario: 移除 Tree 关联
  Given skill = Skill(tree_id=some_uuid)
  When 调用 skill.assign_tree(None)
  Then skill.tree_id 应该为 None
```

---

### 2.2 Tree Aggregate

**源文件**: `app/domain/aggregates/tree.py`

#### 2.2.1 Tree 创建
```gherkin
⬜ 待实现 - tests/unit/domain/aggregates/test_tree.py

Scenario: 创建空 Tree
  When 创建 Tree()
  Then id 应该被自动生成
  And entries 应该为空列表

Scenario: 创建带初始条目的 Tree
  When 创建 Tree(entries=[
    {"path": "README.md", "type": "blob", "blob_id": "..."}
  ])
  Then entries 应该包含一个 TreeEntry
```

#### 2.2.2 add_entry
```gherkin
⬜ 待实现

Scenario: 添加文件条目
  Given tree = Tree()
  When 调用 tree.add_entry("file.txt", "blob", blob_id=uuid)
  Then entries 应该包含 path="file.txt" 的条目
  And 条目类型应该为 "blob"

Scenario: 添加目录条目
  Given tree = Tree()
  When 调用 tree.add_entry("src/", "tree")
  Then entries 应该包含 path="src/" 的条目
  And 条目类型应该为 "tree"
  And blob_id 应该为 None

Scenario: 添加重复路径条目
  Given tree = Tree()
  And tree 已包含 "file.txt"
  When 调用 tree.add_entry("file.txt", "blob")
  Then 应该抛出 ResourceConflictError

Scenario: 添加 blob 条目但不提供 blob_id
  Given tree = Tree()
  When 调用 tree.add_entry("file.txt", "blob", blob_id=None)
  Then 应该抛出 ValidationError（通过 TreeEntry 验证）

Scenario: 添加 tree 条目但提供 blob_id
  Given tree = Tree()
  When 调用 tree.add_entry("src/", "tree", blob_id=some_uuid)
  Then 应该抛出 ValidationError
```

#### 2.2.3 delete_entry
```gherkin
⬜ 待实现

Scenario: 删除文件条目
  Given tree 包含 "file.txt"
  When 调用 tree.delete_entry("file.txt")
  Then entries 不应该再包含 "file.txt"
  And 应该返回包含 blob_id 的列表

Scenario: 删除目录及其子项
  Given tree 包含:
    - "src/"
    - "src/main.py"
    - "src/utils.py"
  When 调用 tree.delete_entry("src/")
  Then 所有 src/ 下的条目都应该被删除
  And 应该返回所有 blob_id

Scenario: 删除不存在的条目
  Given tree 不包含 "nonexistent.txt"
  When 调用 tree.delete_entry("nonexistent.txt")
  Then 应该抛出 ValidationError

Scenario: 尝试删除 SKILL.md
  Given tree 包含 "SKILL.md"
  When 尝试删除 "SKILL.md"
  Then 应该允许删除（业务规则在 Handler 层）
  Note: SKILL.md 保护应该在 Handler 层实现
```

#### 2.2.4 rename_entry
```gherkin
⬜ 待实现

Scenario: 重命名文件
  Given tree 包含 "old.txt"
  When 调用 tree.rename_entry("old.txt", "new.txt")
  Then entries 应该包含 "new.txt"
  And entries 不应该包含 "old.txt"

Scenario: 重命名目录及其子项
  Given tree 包含:
    - "src/"
    - "src/main.py"
    - "src/utils/helper.py"
  When 调用 tree.rename_entry("src/", "lib/")
  Then 应该变为:
    - "lib/"
    - "lib/main.py"
    - "lib/utils/helper.py"

Scenario: 重命名为已存在的路径
  Given tree 包含 "old.txt" 和 "existing.txt"
  When 调用 tree.rename_entry("old.txt", "existing.txt")
  Then 应该抛出 ResourceConflictError

Scenario: 重命名不存在的条目
  Given tree 不包含 "nonexistent.txt"
  When 调用 tree.rename_entry("nonexistent.txt", "new.txt")
  Then 应该抛出 ResourceNotFoundError

Scenario: 使用空字符串作为新名称
  Given tree 包含 "old.txt"
  When 调用 tree.rename_entry("old.txt", "")
  Then 应该抛出 ValidationError

Scenario: 新旧名称相同
  Given tree 包含 "file.txt"
  When 调用 tree.rename_entry("file.txt", "file.txt")
  Then 应该抛出 ValidationError
```

#### 2.2.5 move_entry
```gherkin
⬜ 待实现

Scenario: 移动文件到目录
  Given tree 包含:
    - "file.txt"
    - "dest/"
  When 调用 tree.move_entry("file.txt", "dest/file.txt")
  Then entries 应该包含 "dest/file.txt"
  And entries 不应该包含 "file.txt"

Scenario: 移动目录及其所有内容
  Given tree 包含:
    - "src/"
    - "src/main.py"
    - "src/utils/helper.py"
    - "lib/"
  When 调用 tree.move_entry("src/", "lib/src/")
  Then 应该变为:
    - "lib/"
    - "lib/src/"
    - "lib/src/main.py"
    - "lib/src/utils/helper.py"

Scenario: 移动到已存在的路径
  Given tree 包含 "src/file.txt" 和 "dest/file.txt"
  When 调用 tree.move_entry("src/file.txt", "dest/file.txt")
  Then 应该抛出 ResourceConflictError

Scenario: 移动不存在的条目
  When 调用 tree.move_entry("nonexistent.txt", "dest.txt")
  Then 应该抛出 ResourceNotFoundError

Scenario: 使用空字符串作为目标
  When 调用 tree.move_entry("file.txt", "")
  Then 应该抛出 ValidationError
```

#### 2.2.6 update_entry_content
```gherkin
⬜ 待实现

Scenario: 更新文件内容
  Given tree 包含 "file.txt" (blob_id=old_uuid)
  When 调用 tree.update_entry_content("file.txt", new_uuid)
  Then 条目的 blob_id 应该变为 new_uuid
  And 应该返回 old_uuid

Scenario: 更新目录内容
  Given tree 包含 "src/" (tree 类型)
  When 调用 tree.update_entry_content("src/", some_uuid)
  Then 应该抛出 ValidationError（不能更新目录内容）

Scenario: 更新不存在的文件
  When 调用 tree.update_entry_content("nonexistent.txt", uuid)
  Then 应该抛出 ResourceNotFoundError
```

---

### 2.3 User Aggregate

**源文件**: `app/domain/aggregates/user.py`

#### 2.3.1 User 创建
```gherkin
⬜ 待实现 - tests/unit/domain/aggregates/test_user.py

Scenario: 创建默认用户
  When 创建 User()
  Then id 应该被自动生成
  And is_active 应该为 True
  And email_verified 应该为 False
  And created_at 和 updated_at 应该被设置
```

#### 2.3.2 状态管理
```gherkin
⬜ 待实现

Scenario: 验证邮箱
  Given user = User(email_verified=False)
  When 调用 user.verify_email()
  Then email_verified 应该为 True

Scenario: 停用账户
  Given user = User(is_active=True)
  When 调用 user.deactivate()
  Then is_active 应该为 False

Scenario: 激活账户
  Given user = User(is_active=False)
  When 调用 user.activate()
  Then is_active 应该为 True

Scenario: 修改密码
  Given user = User(password_hash="old_hash")
  When 调用 user.change_password("new_hash")
  Then password_hash 应该为 "new_hash"
  And updated_at 应该更新

Scenario: 更新个人资料
  Given user = User(username="old_name", phone=None)
  When 调用 user.update_profile(username="new_name", phone="123456")
  Then username 应该为 "new_name"
  And phone 应该为 "123456"
  And updated_at 应该更新
```

---

## P1 - Entities

### 3.1 Blob Entity

**源文件**: `app/domain/entities/blob.py`

#### 3.1.1 Blob 创建
```gherkin
⬜ 待实现 - tests/unit/domain/entities/test_blob.py

Scenario: 创建 Blob
  When 调用 Blob.create(b"Hello World")
  Then id 应该被自动生成
  And content 应该为 b"Hello World"
  And content_hash 应该为 SHA256 哈希
  And size 应该为 11
  And compressed 应该为 False
  And reference_count 应该为 0

Scenario: 创建空 Blob
  When 调用 Blob.create(b"")
  Then 应该成功
  And size 应该为 0

Scenario: 创建压缩 Blob
  When 调用 Blob.create(b"Hello World", compressed=True)
  Then compressed 应该为 True
```

#### 3.1.2 引用计数
```gherkin
⬜ 待实现

Scenario: 增加引用计数
  Given blob = Blob()
  When 调用 blob.increment_reference()
  Then reference_count 应该为 1
  
  When 再次调用 blob.increment_reference()
  Then reference_count 应该为 2

Scenario: 减少引用计数
  Given blob = Blob(reference_count=3)
  When 调用 blob.decrement_reference()
  Then reference_count 应该为 2

Scenario: 引用计数归零
  Given blob = Blob(reference_count=1)
  When 调用 blob.decrement_reference()
  Then reference_count 应该为 0
  And blob.is_orphaned() 应该返回 True

Scenario: 引用计数不能为负
  Given blob = Blob(reference_count=0)
  When 调用 blob.decrement_reference()
  Then 应该保持为 0 或抛出异常
```

#### 3.1.3 压缩/解压
```gherkin
⬜ 待实现

Scenario: 压缩 Blob
  Given blob = Blob.create(b"A" * 1000, compressed=False)
  When 调用 blob.compress()
  Then compressed 应该为 True
  And 存储内容应该被压缩

Scenario: 解压 Blob
  Given blob = Blob.create(b"A" * 1000, compressed=True)
  When 调用 blob.decompress()
  Then 应该返回原始内容 b"A" * 1000

Scenario: 获取原始内容（自动解压）
  Given blob = Blob.create(b"Hello", compressed=True)
  When 调用 blob.get_raw_content()
  Then 应该返回 b"Hello"
```

#### 3.1.4 验证
```gherkin
⬜ 待实现

Scenario: 验证内容哈希
  Given blob = Blob.create(b"test")
  When 调用 blob.validate_content()
  Then 应该返回 True

Scenario: 验证损坏的内容
  Given blob = Blob.create(b"test")
  And blob._content 被篡改
  When 调用 blob.validate_content()
  Then 应该返回 False
```

---

## P1 - Factories

### 4.1 SkillFactory

**源文件**: `app/domain/factories/skill_factory.py`

```gherkin
⬜ 待实现 - tests/unit/domain/factories/test_skill_factory.py

Scenario: 创建 Skill
  When 调用 SkillFactory.create(
    user_id=uuid,
    name="Test Skill",
    slug=Slug("test-skill"),
    description="A test"
  )
  Then 应该返回 Skill 对象
  And 所有属性应该正确设置

Scenario: 使用空名称创建 Skill
  When 调用 SkillFactory.create(name="")
  Then 应该抛出 ValidationError

Scenario: 使用超长名称创建 Skill
  When 调用 SkillFactory.create(name="a" * 201)
  Then 应该抛出 ValidationError
```

### 4.2 TreeFactory

**源文件**: `app/domain/factories/tree_factory.py`

```gherkin
⬜ 待实现

Scenario: 创建空 Tree
  When 调用 TreeFactory.create()
  Then 应该返回空 Tree

Scenario: 创建带条目的 Tree
  When 调用 TreeFactory.create(entries=[...])
  Then 应该返回包含条目的 Tree

Scenario: 使用无效条目创建 Tree
  When 调用 TreeFactory.create(entries=[{"invalid": "data"}])
  Then 应该抛出 ValidationError
```

### 4.3 UserFactory

**源文件**: `app/domain/factories/user_factory.py`

```gherkin
⬜ 待实现

Scenario: 创建 User
  When 调用 UserFactory.create(...)
  Then 应该返回 User 对象

Scenario: 验证用户名长度
  When 使用超长用户名
  Then 应该抛出 ValidationError
```

### 4.4 BlobFactory

**源文件**: `app/domain/factories/blob_factory.py`

```gherkin
⬜ 待实现

Scenario: 从内容创建 Blob
  When 调用 BlobFactory.create_from_content(b"data")
  Then 应该返回 Blob 对象

Scenario: 内容哈希计算
  When 创建 Blob
  Then content_hash 应该正确计算
```

---

## 📊 覆盖统计

### 按组件统计

| 组件类型 | 组件数量 | 已测试 | 未测试 | 状态 |
|---------|---------|--------|--------|------|
| Value Objects | 3 | 0 | 3 | 🔴 严重缺失 |
| Aggregates | 3 | 0 | 3 | 🔴 严重缺失 |
| Entities | 1 | 0 | 1 | 🔴 严重缺失 |
| Factories | 4 | 0 | 4 | 🔴 严重缺失 |
| **总计** | **11** | **0** | **11** | **0%** |

### 按方法统计

| 类别 | 方法数量 | 测试优先级 |
|------|---------|-----------|
| Value Object 验证 | 25+ | P0 |
| Aggregate 业务方法 | 20+ | P0 |
| Entity 行为 | 10+ | P1 |
| Factory 创建 | 8+ | P1 |
| **总计** | **63+** | - |

---

## 🎯 实现优先级

### P0 - 立即实现（本周）

1. **Path Value Object**（安全关键）
   - 路径遍历攻击防护测试
   - 边界长度测试

2. **Slug Value Object**（业务关键）
   - 所有验证规则测试
   - from_name 方法测试

3. **Tree Aggregate**
   - add_entry
   - delete_entry
   - rename_entry
   - move_entry

### P1 - 短期实现（2周内）

4. **Skill Aggregate**
   - update_name
   - update_description
   - set_public

5. **Email Value Object**
6. **Blob Entity**
7. **User Aggregate**

### P2 - 中期实现（1月内）

8. **所有 Factories**
9. **相等性和哈希测试**
10. **边界场景完整覆盖**

---

## 🚀 快速开始模板

### 创建 Domain 单元测试文件结构

```bash
mkdir -p tests/unit/domain/{value_objects,aggregates,entities,factories}

touch tests/unit/domain/__init__.py
touch tests/unit/domain/value_objects/__init__.py
touch tests/unit/domain/value_objects/test_slug.py
touch tests/unit/domain/value_objects/test_path.py
touch tests/unit/domain/value_objects/test_email.py

touch tests/unit/domain/aggregates/__init__.py
touch tests/unit/domain/aggregates/test_skill.py
touch tests/unit/domain/aggregates/test_tree.py
touch tests/unit/domain/aggregates/test_user.py

touch tests/unit/domain/entities/__init__.py
touch tests/unit/domain/entities/test_blob.py

touch tests/unit/domain/factories/__init__.py
touch tests/unit/domain/factories/test_skill_factory.py
touch tests/unit/domain/factories/test_tree_factory.py
touch tests/unit/domain/factories/test_user_factory.py
touch tests/unit/domain/factories/test_blob_factory.py
```

### 测试模板示例

```python
# tests/unit/domain/value_objects/test_slug.py
import pytest
from app.domain.value_objects.slug import Slug
from app.domain.exceptions import ValidationError


class TestSlugCreation:
    """Slug 创建测试"""
    
    def test_should_create_slug_with_valid_value(self):
        # Given
        value = "my-test-slug"
        
        # When
        slug = Slug(value)
        
        # Then
        assert slug.value == value
    
    def test_should_convert_to_lowercase(self):
        # Given
        value = "My-Test-Slug"
        
        # When
        slug = Slug(value)
        
        # Then
        assert slug.value == "my-test-slug"
    
    def test_should_raise_error_when_empty(self):
        # When/Then
        with pytest.raises(ValidationError) as exc_info:
            Slug("")
        
        assert "cannot be empty" in str(exc_info.value)
```

---

## P0 - 并发安全测试（新增）

> **说明**: 经 Metis 审核，Domain 层并发安全是系统稳定性的关键，需要专门测试

### 5.1 Blob 引用计数并发安全

**源文件**: `app/domain/entities/blob.py`

```gherkin
⬜ 待实现 - tests/unit/domain/concurrency/test_blob_concurrency.py

Scenario: 并发增加引用计数
  Given Blob blob_ref 当前引用计数为 0
  When 10 个并发线程同时调用 increment_reference()
  Then 最终引用计数应该为 10
  And 不应该出现竞态条件导致的计数错误

Scenario: 并发减少引用计数
  Given Blob blob_ref 当前引用计数为 10
  When 10 个并发线程同时调用 decrement_reference()
  Then 最终引用计数应该为 0
  And is_orphaned() 应该返回 True

Scenario: 并发混合操作引用计数
  Given Blob blob_ref 当前引用计数为 5
  When 5 个线程增加引用
  And 3 个线程减少引用
  Then 最终引用计数应该为 7（5 + 5 - 3）
  And 操作结果应该是确定性的
```

### 5.2 Tree 条目操作并发安全

**源文件**: `app/domain/aggregates/tree.py`

```gherkin
⬜ 待实现

Scenario: 并发添加相同路径条目
  Given Tree 为空
  When 两个并发线程同时添加 "file.txt"
  Then 只有一个应该成功
  And Tree 中应该只有一条 "file.txt" 记录
  And 另一个应该抛出 ResourceConflictError

Scenario: 并发删除同一文件
  Given Tree 包含 "file.txt"
  When 两个并发线程同时删除 "file.txt"
  Then 第一个应该成功
  And 第二个应该抛出 ResourceNotFoundError（或 ValidationError）
  And Blob 引用计数应该只减少一次

Scenario: 并发重命名和删除同一文件
  Given Tree 包含 "old.txt"
  When 线程 A 重命名 "old.txt" 为 "new.txt"
  And 线程 B 同时删除 "old.txt"
  Then 操作结果应该是确定性的
  And Tree 状态应该保持一致（不能同时存在和不存在）
```

### 5.3 Skill 版本更新并发安全

**源文件**: `app/domain/aggregates/skill.py`

```gherkin
⬜ 待实现

Scenario: 并发更新 Skill 元数据
  Given Skill 版本为 1
  When 两个并发线程同时调用 update_name()
  Then 两个操作都应该成功（乐观锁策略）
  And Skill 版本应该变为 3（每次更新都增加版本）
  And 最终 name 应该是最后完成的那个线程的值

  Or（悲观锁策略）
  Then 第一个操作成功，版本变为 2
  And 第二个操作应该抛出 ResourceConflictError
  And 第二个线程应该获取最新版本重试
```

---

**文档版本**: 1.0（Metis 审核后修订版）  
**生成时间**: 2026-02-20  
**当前 Domain 测试覆盖率**: **0%**（严重缺失）  
**目标覆盖率**: 95%（需实现 63+ 个测试方法）  
**建议优先级**: 🔴 **最高** - Domain 层是核心业务逻辑，必须优先补充单元测试
