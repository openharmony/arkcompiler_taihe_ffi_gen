# Backend 阶段模型与 Options 系统设计报告

## 背景与问题

### 旧架构的临时方案

在 ANI 后端中，需要通过以下三个编译选项来控制代码生成行为：

- `sts:keep-name`：是否保留原函数名（不做 camelCase 转换）
- `arkts:module-prefix`：ArkTS 模块前缀，影响 ANI 类型签名
- `arkts:path-prefix`：ArkTS 路径前缀，同样影响 ANI 类型签名

这些选项被消费的时间节点并不在命令行解析阶段——它们被 Analysis 系统使用。具体来说，`PackageAniInfo` 在构造时需要根据 `keep-name` 决定命名策略，而 `ArkTsOutDir`（负责计算 ANI 符号的模块路径）依赖 `module-prefix` 和 `path-prefix`。

旧实现的做法是：在 `CompilerInstance` 构造时，把命令行的 raw config dict 解析成一个 `CompilerConfig` 对象（硬编码了 `sts_keep_name`、`arkts_module_prefix`、`arkts_path_prefix` 三个字段），然后把这个 `CompilerConfig` **直接塞进 `AnalysisManager` 中**：

```python
class CompilerConfig:                               # 硬编码，TODO: refactor this
    sts_keep_name: bool = False
    arkts_module_prefix: str | None = None
    arkts_path_prefix: str | None = None

class AnalysisManager:
    config: CompilerConfig                          # hack: 与后端逻辑耦合
    def __init__(self, config): ...

class ArkTsOutDir:
    def _create(cls, am, pg):
        ...
        bundle_str = am.config.arkts_module_prefix  # hack
        prefix_str = am.config.arkts_path_prefix    # hack
```

这种做法的问题：
1. **不可扩展**：新后端的选项只能继续往 `CompilerConfig` 里塞字段，或者再 hack 一个新的存储位置。
2. **选项验证缺失**：`CompilerConfig.construct()` 用字符串 `if-elif` 匹配选项名，拼写错误不会报错（只会被 `else: raise` 兜底），也没有 fuzzy matching 提示。且没有统一的类型系统来约束选项值的类型和合法性。
3. **AnalysisManager 与后端逻辑耦合**：`AnalysisManager` 是基础设施组件，持有某个特定后端的配置类型是职责越界。

### 核心矛盾

问题的本质是一个信息流向冲突：**选项由后端定义和消费，但选项的值需要在 Analysis 阶段（由 AnalysisManager 管理的缓存体系）被访问。**

合理的所有权是：后端注册选项 → 解析后由后端的 `BackendConfig` 持有 → 在后端的生命周期内使用。但 Analysis 是惰性求值、按需创建的，它没有直接的通道拿到 `BackendConfig` 上的字段。

---

## 方案探索与权衡

### 方案 0：OptionStore 存入 AnalysisManager / PackageGroup

加一个 `OptionRegistry` 注册系统，但仍然把解析后的强类型的 `OptionStore` 整体塞进 `AnalysisManager`（或 `PackageGroup` / `CompilerInstance`）供 Analysis 读取。

这本质上是旧做法的类型安全版——`AnalysisManager.config` 从 `CompilerConfig` 变成强类型、可扩展的 `OptionStore`，但耦合关系并未解除。对于 `module-prefix` 和 `path-prefix`，把它们视为 PackageGroup 的附加属性存入 `PackageGroup` 似乎语义上说得通（它们确实描述了一组 package 的部署路径），但这会给 `PackageGroup` 开一个口子，使其承载越来越多与 IR 无关的元信息。

### 方案 1：BackendConfig 消费后冗余存储

`BackendConfig.create()` 消费选项后，再把 `OptionStore` 冗余地存进 `CompilerInvocation`。Analysis 通过 `CompilerInstance` → `CompilerInvocation` → `OptionStore` 访问。

问题是 `CompilerInvocation` 的定位是**命令行意图的结构化表示**，它不应该携带已经被消费过的 raw options。当未来支持配置文件（比如 `taihe.toml`）时，如果遇到 `OptionStore` 和 `BackendConfig` 中同一选项的值不一致的情况，会产生「who is the source of truth」的问题。

### 方案 2：只在 BackendConfig 中消费，通过某种机制传回

这是最终的方向，但这个方案的难点在于如何在 Analysis 需要时把 `BackendConfig` 中的选项值传递给它。以下是几个备选方案：

**(2.1) 在构造 Analysis 时传入 Option。** 即 `ArkTsOutDir.get(am, pg, options, ...)`。但这破坏了 Analysis 缓存的语义——Analysis 应该和特定的 Declaration 绑定。将 options 同时作为 Key 的一部分并没有意义，因为在一次编译中不可能出现同一个 Declaration 对应多个不同 options 的情况。另外，这种调用方式也会增加使用复杂度，所有调用 `Analysis.get()` 的地方都需要传入 options。

**(2.2) Analysis 不缓存，变成纯函数。** 即 `ArkTsOutDir.compute(pg, options) -> result`，调用方每次传入 options 计算。这放弃了 Analysis 系统的核心价值——缓存和去重。而且 Analysis 之间存在依赖链（`PackageAniInfo` → `PackageGroupAniInfo` → `ArkTsOutDir`），这种方案的传染性会导致所有依赖了选项的 Analysis 都需要在调用时手动传入 options，极大增加使用复杂度。

**(2.3) Backend 在特定阶段将信息注入回 AnalysisManager 或 IR。** 最终选定的方案。

---

## 最终方案：注入式传递

### Options 系统

引入三个组件：

| 组件 | 职责 |
|---|---|
| `AbstractConfigOption` | 选项的类型定义。每个子类通过 `NAME` 声明命令行名称，通过 `parse(value, diag_mgr)` 实现类型安全的解析逻辑。 |
| `OptionRegistry` | 解析期的编译选项注册表。由后端自己注册支持的编译选项类型。将 option name 映射到 option type，支持 fuzzy matching 错误提示。 |
| `OptionStore` | 解析结果的存储。multimap 结构 `dict[type, list[option]]`，支持 `get`（单值）和 `get_all`（多值）。 |

`OptionStore` 的 multimap 设计参考了声明上 Attribute 的存储方式——同一类型的选项可以出现多次（虽然当前的三个 ANI 选项都是单值的，但这为未来的 `--include-path` 类选项预留了空间）。

### 完整传递路径

```
opt_reg = OptionRegistry()                                  # 创建 OptionRegistry 实例
  ↓
BackendConfig.register(opt_reg)                             # 后端声明「自己需要哪些选项」
  ↓
opts: OptionStore = opt_reg.parse_args(args, diag_mgr)      # 统一解析，未知选项报错 + fuzzy suggest
  ↓
conf: BackendConfig = BackendConfig.create(opts, diag_mgr)  # OptionStore 被 BackendConfig 工厂方法消费用于构造实例
  ↓
comp_inv = CompilerInvocation(backend_configs=[conf, ...])  # BackendConfig 作为 CompilerInvocation 的一部分
  ↓
comp_ins = CompilerInstance(comp_inv, diag_mgr)             # 根据 CompilerInvocation 构造 CompilerInstance
  ↓
backend: Backend = conf.construct(comp_ins)                 # 在 CompilerInstance 中，根据 BackendConfig 构造 Backend 实例
  ↓
Backend.register()                                          # 在此阶段将选项值注入回系统
  └─ ArkTsOutDir.provide(...)                               # module-prefix/path-prefix -> Analysis 缓存
  ↓
Backend.post_process()                                      # 在此阶段将选项物化为 IR 注解
  └─ decl.add_attribute(...)                                # keep-name -> per-package 属性
```

命令行参数可能存在输入错误的情况，在以上流程中，有两个阶段允许通过诊断器报告错误：

1. `AbstractConfigOption.parse()`：针对单个选项值的解析错误（如类型错误、格式错误），可以在这里直接报告。错误应该通过 `DiagnosticsManager` 发出，并且 `parse()` 返回 `None`。不应该抛出异常。
2. `BackendConfig.create()`：针对选项间的组合逻辑错误可以在这里报告（如互斥选项同时出现、必需选项缺失等）。报告方式同上。

除此之外，不应该在后续阶段，尤其是通过 `BackendConfig` 构造 `Backend` 实例时再报告选项相关的错误。换句话说，`BackendConfig` 的合法性应该在 `create()` 阶段被完全验证，`construct()` 阶段不应再担心选项错误的情况。

### `Analysis.provide` 和 `AnalysisManager.provide` 的设计

`provide` 方法是这套方案的关键拼图。它的作用是：**在 Analysis 的缓存中预置一个由外部构造的实例，使得后续通过标准的 `Analysis.get()` API 访问时，直接命中这个预置值，而不走 `_create()` 工厂方法。**s

```python
class AbstractAnalysis(Generic[H], ABC):
    @classmethod
    def provide(cls: type[A], am: AnalysisManager, arg: H, instance: A) -> None:
        am.provide(cls, arg, instance)

class AnalysisManager:
    def provide(self, analysis_type: type[A], arg: Hashable, analysis: A) -> None:
        key = CacheKey(analysis_type, arg)
        self._cache[key] = analysis
```

这个模式可以类比为依赖注入框架中的 `bind(type).toInstance(instance)`——在正常的惰性求值流程之外，显式地为某个 key 绑定一个已构造好的值。与依赖注入框架不同的是，这里的 key 不仅包含类型，还包含参数（比如 `PackageGroup` 实例），因此同一类型的 Analysis 在不同参数下可以有不同的绑定。LLVM 的 `AnalysisManager` 也提供了类似功能。

对于被 `provide` 注入的 Analysis，其 `_create()` 方法实现为 `raise NotImplementedError`。这是一个有意的设计：如果后端忘记调用 `provide`，任何试图通过 `Analysis.get()` 获取该 Analysis 的代码都会立即得到一个明确的错误，而不是悄悄地使用某个默认值。

`provide` 的语义约束：
1. `provide` 应当在 `register()` 阶段调用——此时 IR 尚未解析，Analysis 缓存为空，不存在 key 冲突的可能。
2. 由于 1 中的时机限制，`provide` 注入的 Analysis 只能是 `PackageGroup` 粒度的（因为 `PackageDecl` 还不存在）。如果需要更细粒度的注入（如 per-package 的 `keep-name`），应当考虑在 `post_process()` 阶段通过添加属性的方式实现。

### `keep-name` 的演化：从 Analysis 到 Attribute

`keep-name` 选项经历了两次设计变更，反映了对配置信息归属的逐步认识。

**第一版：** `keep-name` 和 `module-prefix`/`path-prefix` 一样，被包装成 `ArkTsNamingConfig` Analysis，在 `register()` 阶段通过 `provide` 注入。`PackageAniInfo` 构造时从 `ArkTsNamingConfig.get(am, pg)` 获取命名策略。

这个方案可以工作，但存在粒度问题：`ArkTsNamingConfig` 是绑定到整个 `PackageGroup` 的，意味着所有 package 共享同一个命名策略。如果未来需要**某个 package 保留原名、其它 package 使用 camelCase**，这个设计无法支持。

**第二版：** 将 `keep-name` 从全局 Analysis 改为 per-package 的 `@sts_keep_name` 属性。`-Carkts:keep-name` 命令行选项在 `post_process()` 阶段被物化为每个 Package 上的 `StsKeepNameAttr`：

```python
def post_process(self):
    if self._config.keep_name:
        for p in self._ci.package_group.packages:
            if StsKeepNameAttr.get(p) is None:          # 幂等：已有则跳过
                p.add_attribute(StsKeepNameAttr(loc=p.loc))
```

`PackageAniInfo` 不再查询全局 Analysis，而是直接检查当前 package 上是否有 `@sts_keep_name` 属性：

```python
if (attr := StsKeepNameAttr.get(p)) and attr.option:
    self.naming = UnchangeNamingStrategy()
```

这个转变的意义：

1. **粒度提升**：用户可以在 IDL 中为单个 package 写 `@sts_keep_name`，实现 per-package 的命名策略控制，与全局的 `-C` 选项共存。
2. **可序列化**：命令行选项是运行时的、瞬态的，而属性是 IR 的一部分，可以被保存和重新加载。当 `post_process()` 将选项物化为属性后，IR 就完整地记录了所有影响代码生成的信息。
3. **关注点分离**：`module-prefix`/`path-prefix` 保持为 Analysis，因为它们描述的是部署环境的全局属性（整个 PackageGroup 共享一套路径方案），不存在 per-package 差异化的合理场景。而 `keep-name` 本质上是对命名约定的偏好，per-package 粒度更自然。

**为什么 `module-prefix`/`path-prefix` 没有也转为 Attribute？** 因为它们是构建环境参数（类似 C 编译器的 `-I` include path），而非 IDL 源码中应该出现的声明性注解。将它们写进 IDL 会导致源码与构建环境耦合。

---

## Backend 阶段模型

`CompilerInstance.run()` 驱动以下阶段：

```
construct → register → collect/inject → parse/post_process → validate → generate
```

每个阶段对后端开放了特定的钩子。以下分析各阶段的目的、约束及其设计理由。

### `register()`

**时机**：Backend 实例构造之后、IR 解析之前。

**用途**：
- 注册后端特有的 Attribute 类型到 `AttributeRegistry`
- 通过 `provide` 预置配置型 Analysis
- 任何后端初始化相关的一次性工作

**约束**：
- **不应影响其它后端的 Analysis 结果。** `provide` 注入的 Analysis 应当使用后端特有的 Analysis 类型，而非覆盖已有的公共 Analysis。
  - **理由**：register 发生在所有 Backend 构造完成之后（`CompilerInstance.__init__` 先构造所有 Backend，再逐一调用 `register()`），但各 Backend 的 register 顺序依赖于 `collect_required_backends` 的 DFS 遍历顺序。如果一个 Backend 的 register 能影响另一个 Backend 的 Analysis，就会引入对注册顺序的隐式依赖。

### `inject()`

**时机**：`collect()` 阶段的末尾，源文件扫描完成之后，AST 构建之前。

**用途**：向 `SourceManager` 添加后端需要的额外源文件。某些后端需要引入专有的标准库（比如 ANI 后端的 `taihe.platform.ani.taihe`），这些定义不应该被编译器核心无条件引入，而是按需由启用的后端注入。

### `post_process()`

**时机**：`parse()` 完成（IR 已构建）之后、语义分析之前。

**用途**：在 IR 上添加后端特有的元数据（属性）。典型场景：将命令行选项物化为 per-declaration 的属性。

**约束（及理由）**：

1. **必须幂等。** 如果将 `post_process()` 修改后的 IR 保存并重新编译，`post_process()` 会再次执行。如果非幂等（例如每次追加一个属性而不检查已有），就会产生与编译次数相关的非确定性结果。实际实现中通过 `if StsKeepNameAttr.get(p) is None` 的前置检查保证幂等。

2. **不得修改 IR 结构本身（声明、类型等），只能添加后端特有属性。** 这是为了保证**后端隔离性**：开启后端 A 不应改变后端 B 看到的 IR 形态。如果 `post_process` 允许修改声明结构（比如添加/删除函数参数），那么后端 B 的代码生成可能因为后端 A 的存在而产生不同结果——这违反了「后端是代码生成的平行输出通道」的基本假设。

3. **不得修改其它后端的属性或公共属性。** 同样是后端隔离性的推论。如果后端 A 能修改后端 B 的属性，就需要指定 `post_process` 的执行顺序，引入后端间的隐式耦合。当前设计明确声明**执行顺序未定义**，迫使各后端独立工作。

4. **不得依赖其它后端的 `post_process` 结果。** 这是上一条约束的逻辑延伸——既然不能修改别人的属性，也就没有依赖别人修改的理由。

### `validate()`

**时机**：语义分析完成之后。

**用途**：检查后端特有属性的使用是否正确。例如 `@async` 不能标注在返回 void 的函数上。

**约束（及理由）**：

1. **不得修改 IR。** `validate()` 是纯只读的诊断阶段。如果允许在验证时修改 IR，就会模糊 `post_process`（修改）和 `validate`（检查）的职责边界，且修改与诊断交织会使错误报告的正确性难以保证。

2. **开启后端不得导致原本合法的代码报错。** 这是一个关键的用户体验约束：用户的 IDL 源码在不开启 ANI 后端时能编译通过，那么仅仅因为加了 `-G ani-bridge` 就报错是不可接受的。换句话说，**一个不带任何后端特定注解的 IR 必须能被所有后端正确处理**。

   这个约束直接决定了 `validate()` 的检查范围：只检查后端特有属性。如果代码没有使用任何 ANI 特有属性（如 `@namespace`、`@async`），则 ANI 后端的 `validate()` 必须静默通过。

3. **优先使用 `Attribute.check_context()` 而非 `validate()` 做属性级检查。** `check_context()` 是在属性解析时由 `AttributeRegistry` 自动调用的，它确保属性的目标类型正确（比如 `@namespace` 只能用在 PackageDecl 上）。只有涉及跨属性/跨声明的复杂校验（比如检查一个 `Package` 内的所有声明间是否存在冲突），才需要在 `validate()` 中实现。

### `generate()`

**时机**：所有验证通过后（如果有错误则跳过）。

**用途**：生成输出文件。

**约束**：
1. **不得修改 IR。** 代码生成是终端操作，它的输入应该是完全确定的 IR。
2. **不得报告错误。** 所有可能的错误应在 `validate()` 阶段已经被捕获。如果在 `generate()` 中才发现错误，说明 `validate()` 的检查不充分。

---

## 约束体系的统一分析

上述各阶段的约束不是孤立制定的，它们服务于几个核心设计原则：

### 后端隔离性

**原则**：开启后端 A 不影响后端 B 的行为。

**推论**：
- `post_process` 不修改 IR 结构（否则 B 看到的 IR 不同）
- `post_process` 不修改其它后端的属性（否则 B 的属性被篡改）
- `validate` 不因为无关属性报错（否则 B 的存在导致 A 的代码失败）
- `register` 的 `provide` 只注入自己的 Analysis 类型

这个原则确保了后端是可组合的——用户可以同时开启多个后端（如 `ani-bridge` + `cpp-user`），效果等价于分别开启各后端的结果的并集。

### 后端透明性（待定）

**原则**：编译器不应因为后端的存在而引入新的错误，除非用户使用了后端特有的注解。

**推论**：`validate` 只应因「错误使用注解」报错，不应因「没有使用注解」而报错，即应提供「无任何后端特有注解」时的默认行为。

### 注解透明性

**原则**：注解（后端特有属性）不影响 ABI 层和核心层的代码生成。

**推论**：所有注解只被定义它的后端读取，ABI/core 代码生成对注解无感。这确保了核心 C ABI 的稳定性——无论 IDL 上标注了什么 ArkTS 特有注解，生成的 C header 和 ABI source 不会改变。

### IR 可重入性

**原则**：`post_process` 修改后的 IR 被保存再重新编译，结果应与修改前一致（除了注解的增加）。

**推论**：
- `post_process` 必须幂等（重复执行不改变结果）

### 阶段单调性

**原则**：信息在编译流水线中单向流动，后面的阶段不修改前面阶段的产物。

```
register → inject → post_process → validate → generate
                          ↓
                    (仅添加属性)
                                       ↓
                                 (仅读取+诊断)
                                                  ↓
                                            (仅读取+输出)
```

这确保了在任意阶段，之前阶段的产物是稳定的、可信赖的。`validate` 可以安全地假设 IR 不会再变化；`generate` 可以安全地假设不会再有新的错误被报告。

---

## 小结

Options 系统的重构解决了「编译选项如何正确地流向 Analysis 系统」这个问题。最终方案的核心思路是**让后端自己在恰当的阶段将配置信息注入回系统**，而非让系统反向持有后端的配置。这个方向上又进一步区分了两类配置信息的归属：

- **环境参数**（`module-prefix`、`path-prefix`）：通过 `provide` 注入 Analysis，绑定到 PackageGroup 粒度。这类信息描述的是部署环境而非源码语义，不适合作为 IDL 属性。
- **可作为声明附加信息的属性**（`keep-name`）：在 `post_process` 阶段物化为 per-package 属性。这类信息可以被 IDL 作者在源码中 per-package 覆盖，全局命令行选项只是提供了一个默认值。
- 此外也可以影响后端的初始化、注解和标准库的启用、诊断、代码生成等行为。根据具体情况、怎样更易于实现和使用决定。

同时，Backend 阶段模型通过精确定义每个阶段的可操作范围和约束条件，确保了多后端并存时的隔离性、可组合性和可预测性。
