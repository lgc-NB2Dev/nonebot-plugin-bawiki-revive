<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-BAWiki-Revive

_✨ 蔚蓝档案综合插件，堂堂复活（并没完全复活） ✨_

<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<a href="https://github.com/astral-sh/uv">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/b9ad9c44-d425-45e9-b39d-6459107e02dd">
  <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/b9ad9c44-d425-45e9-b39d-6459107e02dd.svg" alt="wakatime">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lgc-NB2Dev/nonebot-plugin-bawiki-revive.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-bawiki-revive">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-bawiki-revive.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-bawiki-revive">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-bawiki-revive" alt="pypi download">
</a>

<br />

<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-bawiki-revive:nonebot_plugin_bawiki_revive">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-bawiki-revive" alt="NoneBot Registry">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-bawiki-revive:nonebot_plugin_bawiki_revive">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin-adapters%2Fnonebot-plugin-bawiki-revive" alt="Supported Adapters">
</a>

</div>

## 📖 介绍

什么？BAWiki 复活了（但是好像并没有完全活）

当前版本主要提供 Arona 攻略数据源查询功能。

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行，输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-bawiki-revive
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下，打开命令行，根据你使用的包管理器，输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-bawiki-revive
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-bawiki-revive
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-bawiki-revive
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-bawiki-revive
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件，在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_bawiki_revive"
]
```

</details>

## ⚙️ 配置

在 NoneBot2 项目的 `.env` 文件中添加下表中的配置

|                 配置项                  | 必填 | 默认值  |                     说明                     |
| :-------------------------------------: | :--: | :-----: | :------------------------------------------: |
|              **通用配置**               |      |         |                                              |
|      `BAWIKI_REV_REQUEST_TIMEOUT`       |  否  | `10.0`  |              请求超时时间（秒）              |
|   `BAWIKI_REV_REQUEST_RETRY_ATTEMPTS`   |  否  |   `3`   |               请求失败重试次数               |
|     `BAWIKI_REV_REQUEST_RETRY_WAIT`     |  否  |  `1.0`  |            每次请求重试前等待时间            |
|             **Arona 配置**              |      |         |                                              |
|     `BAWIKI_REV_ARONA_API_BASE_URL`     |  否  |   ...   |               Arona API 基地址               |
|     `BAWIKI_REV_ARONA_CDN_BASE_URL`     |  否  |   ...   |            Arona 图片 CDN 基地址             |
|     `BAWIKI_REV_ARONA_SEARCH_SIZE`      |  否  |   `8`   |              模糊搜索返回结果数              |
|    `BAWIKI_REV_ARONA_SEARCH_METHOD`     |  否  |   `3`   |   Arona 模糊搜索方法，详见 Arona API 文档    |
|      `BAWIKI_REV_ARONA_FILTER_R18`      |  否  | `True`  |            默认是否过滤 R18 结果             |
|   `BAWIKI_REV_ARONA_ALLOW_R18_PARAM`    |  否  | `False` |      是否允许用户通过 `--r18` 查询 R18       |
| `BAWIKI_REV_ARONA_ALIAS_ONLY_SUPERUSER` |  否  | `False` |          是否仅允许超级用户管理别名          |
|    `BAWIKI_REV_ARONA_SELECT_TIMEOUT`    |  否  | `60.0`  | 等待用户输入关键词或选择结果的超时时间（秒） |

## 🎉 使用

### PicMenu Next 集成

推荐搭配 [PicMenu Next](https://github.com/lgc-NB2Dev/nonebot-plugin-picmenu-next) 插件使用

安装并加载 `nonebot_plugin_picmenu_next` 后，本插件会与其联动，注册 `bawiki_revive` 菜单模板。

该菜单模板是为 BAWiki Revive 单独准备的，包含首页、插件详情页和功能详情页。插件自身的详情页与功能详情页会默认使用它。

此模板 99% 由 AI 设计，剩余 1% 为人工微调。

如果想让 PicMenu 首页使用这套模板，可配置：

```properties
PMN_INDEX_TEMPLATE=bawiki_revive
```

如果想让其他插件的详情页和功能详情页也使用这套模板，可继续配置：

```properties
PMN_DETAIL_TEMPLATE=bawiki_revive
PMN_FUNC_DETAIL_TEMPLATE=bawiki_revive
```

<details>
<summary>首页示例（点击展开/收起）</summary>

![index sample](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/bawiki-revive/index_sample.jpg)

</details>

<details>
<summary>详情页示例（点击展开/收起 可以查看本插件功能列表）</summary>

![detail sample](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/bawiki-revive/detail_sample.jpg)

</details>

<details>
<summary>功能详情页示例（点击展开/收起）</summary>

![func detail sample](https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/bawiki-revive/func_detail_sample.jpg)

</details>

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[168603371](https://qm.qq.com/q/EikuZ5sP4G)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [Arona Bot 攻略数据公开计划](https://doc.arona.diyigemt.com/v1/api/)

- Arona Bot 数据源

## 💰 赞助

**[赞助我](https://blog.lgc2333.top/donate)**

感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📝 更新日志

芝士刚刚发布的插件，还没有更新日志的说 qwq~
