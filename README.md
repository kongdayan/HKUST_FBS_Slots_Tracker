# HKUST_FBS_Slots_Tracker

# 抢场地通知系统

一个自动从不同平台获取场地信息，并通过各种方式进行通知的系统。

## 特点

- 支持从多个平台（如`alumni`）获取场地信息。
- 当找到可用的场地时，可以通过多种渠道（如`pushdeer`，`feishubot`，`larkbot`）发送通知。
- 自定义时间范围，只关心特定时间段内的场地。
- 当API凭证过期时，系统会发送维护通知。

## 安装

1. 克隆此仓库：

```
git clone <git@github.com:kongdayan/FBS_HKUST_Spider.git>
```

2. 进入项目目录：

```
cd <git@github.com:kongdayan/FBS_HKUST_Spider.git>
```

3. 安装所需的依赖：

```
pip install -r requirements.txt
```

## 配置

1. 复制`.env.example`到`.env`：

```
cp .env.example .env
```

2. 使用您的配置信息编辑`.env`文件。
3. 根据需要编辑`config.py`，设置你关心的时间范围。

## 使用

运行`main.py`开始抢场地：

```
python main.py
```

系统会定期检查指定平台上的场地信息，并在找到可用场地时发送通知。

## 贡献

欢迎对此项目进行贡献。请提交Pull Request或在issue区域中报告任何问题。

## 许可证

此项目使用MIT许可证。
