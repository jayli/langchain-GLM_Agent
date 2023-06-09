# 本地知识库大模型 langchain + chatglm + Custom Agent

langchain + chatgpt 的 agent 真香，实现了一个简单的基于 chatglm 的 custom agent。支持本地知识库和联网检索。llm 也是自定义，如果想改成 openAI 也可以。

详细介绍参照这里：<https://zhuanlan.zhihu.com/p/635724707>

## 介绍

langchain 的 agent 设计的非常聪明，但这个“聪明”是基于 chatgpt 强大的理解力，agent 自带的 prompt 并不能被 chatglm-6b 很好的理解，主要是 Action 字段和 Input 字段总是出错，所以我针对 chatglm 写了一个简单的 custom agent，不能做到 100% 的 prompt 指令精确响应，我实测 80% 的情况下可以正确响应，结合 Tool 能实现一些复杂的应用。

## 硬件部署

这里没有在本地跑大模型，所以硬件条件基本上不限制。

## 准备工作

1. 部署你的 chatglm 大模型，确保可以 api 调用，修改 `models/custom_llm.py` 里 `_call` 方法里的调用地址，或者你用 openAI 代替也可以，参照 [langchain 官网文档](https://python.langchain.com/)
1. `models/custom_search.py` 中设置你的 `RapidAPIKey = ""`，[申请步骤异步这里](https://rapidapi.com/microsoft-azure-org-microsoft-cognitive-services/api/bing-web-search1)（接口名字可以搜索：`bing-web-search1`）

代码checkout下来后，执行

```
python helloworld.py
```

有正常的返回就ok了。

## 启动

```
python server.py
```

启动服务监听 8899 端口，这样访问：

```
curl -d "ask=helloworld1" \
    -H "Content-Type: application/x-www-form-urlencoded"  \
    -X POST http://127.0.0.1:8899/ai/langchain/
```

结果返回

```
{"content":"\u60a8\u9700\u8981\u9884\u5b9a\u673a\u7968\u5417?","status":200}
```

注意：

- curl 命令中传参数不要有空格，如果需要测试最好用 postman 之类的工具
- server 启动用的 flask，如果需要其他机器访问，修改server.py 中服务启动加上本地 host：`app.run(debug=False, port=8899, host="192.168.0.11")`

## 例子

这是一个实际的例子：执行`python cli.py`

```
> Entering new AgentExecutor chain...
DeepSearch('携程最近有什么大新闻？')

Observation:到中国旅游更偏爱小红书 马来西亚年轻人对携程没兴趣: 【蓝科技观察】小红书成为马来西亚年轻人了解中国旅游市场的首选，而不是中国旅游平台携程。在马来西亚年轻人尤其是华人看来，携程的商业属性更明显，而小红书则能给他们带来更多的价值。 最近，马来西亚第四代华人Emma计划来中国旅游，而她是通过小红书来了解中国的旅游、文化、时尚等信息。 “按照我的思路，获得我想要的结果。”Emma表示，如她一样喜欢旅游的年轻人在马来西亚比比皆是，他们在小红书上follow热
携程：每10人有1人游览博物馆 00后文博爱好者增速最快: 随着“5.18国际博物馆日”临近，根据博物馆预订人次，结合线上搜索热度及馆藏数量，携程口碑榜发布了“国内博物馆20佳”，分别是：故宫、中国 ...
十人就有一人逛博物馆 携程口碑榜发布“国内博物馆20佳”: 近期，携程还与浦东美术馆合作，正式开启人工讲解服务，包含快速入场通道、配套耳麦设备、专人接待讲解等多项特别礼宾服务。除了为观众深入讲述馆内展览与重要展品背后的故事，还将全方位介绍美术馆建筑设计及功能空间的独到之处，让艺术不再“有 ...
出国热又起，各大领馆一约难求，堪比春节抢票？！有的地方拒签率 ...: 上海新闻广播微信公众号消息，积压了整整三年的旅游热情，终于在今年有了可“用武之地”，被戏称为“最强五一”的旅游 ...
根据已知信息，携程最近在博物馆预订方面取得了显著进展，每10人有1人游览博物馆，00后文博爱好者增速最快。此外，携程还与浦东美术馆合作，开启了人工讲解服务，并提升了博物馆服务质量。这些新闻表明携程在旅游业领域继续扩大其影响力，并不断提升服务质量，以满足消费者的需求。

> Finished chain.
根据已知信息，携程最近在博物馆预订方面取得了显著进展，每10人有1人游览博物馆，00后文博爱好者增速最快。此外，携程还与浦东美术馆合作，开启了人工讲解服务，并提升了博物馆服务质量。这些新闻表明携程在旅游业领域继续扩大其影响力，并不断提升服务质量，以满足消费者的需求。
```

