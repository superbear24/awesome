# 多级依赖注入器

- Angular 是一个多级依赖注入系统
- 应用程序中有一个与组件树结构完全相同且一一对应的注入器树，可以在组件书中的任何级别上重新配置注入器

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

* [多级依赖注入器](#多级依赖注入器)
	* [注入器树](#注入器树)
		* [注入器冒泡](#注入器冒泡)
		* [在不同层级再次提供同一个服务](#在不同层级再次提供同一个服务)
	* [组件注入器](#组件注入器)
		* [服务隔离](#服务隔离)
		* [多重编辑会话](#多重编辑会话)
		* [专门的提供商](#专门的提供商)

<!-- /code_chunk_output -->

## 注入器树

 * 一个应用可能有多个注入器
 * 每个组件都有自己的注入器

[Back To TOC](#多级依赖注入器)

### 注入器冒泡

 * 当一个组件申请获得一个依赖时，Angular 先尝试试用改组件自己的注入器来满足它
 * 如果改组建的注入器没有找到对应的提供商，就把这个申请转给它父组件的注入器来处理
 * 如果父组件注入器也无法满足这个申请，它就继续转给它的父组件的注入器
 * 这个申请继续往上冒泡，知道到注入器或者到达祖先位置
 * 如果达到祖先还未找到，则抛出错误

[Back To TOC](#多级依赖注入器)

### 在不同层级再次提供同一个服务

 * 在注入器树中的多个层次上为指定的依赖令牌重新注册提供商，但是不建议这个做
 * 服务会自下而上查找，遇到异地个提供商会胜出
 * 在根模块 AppModule 中提供的服务能够被整个应用使用

[Back To TOC](#多级依赖注入器)

## 组件注入器
 
 * 在不同的层次上重新配置一个或多个提供商的能力

[Back To TOC](#多级依赖注入器)

### 服务隔离

 * 在组件的元数据中提供服务，限时服务只能在该组件中使用

```ts
// app/villains-list.component.ts
@Component({
  selector: 'app-villains-list',
  templateUrl: './villains-list.component.html',
  providers: [ VillainsService ]
})
```

[Back To TOC](#多级依赖注入器)

### 多重编辑会话

 * 同事进行多个任务时，保证每个任务互不影响，将任务可能会影响的部分拆成服务独立出来注入使用

[Back To TOC](#多级依赖注入器)

### 专门的提供商

 * 为组件定制自己的提供商

[Back To TOC](#多级依赖注入器)