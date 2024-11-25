# 介绍
为了在windows系统上模拟linux命令，依靠强大的prompt_toolkit工具，开发了一套mini操作系统，支持输入高亮、智能命令补全等比原生git bash更强大的功能，但是还是有很多bug没解决。

# 环境安装
仅依赖prompt-toolkit工具，纯python代码
```pip install prompt_toolkit```

# 启动脚本
运行main.py即可
```python main.py```

- 支持输入命令高亮
![11月25日(2)](https://github.com/user-attachments/assets/d7912abc-7c6f-4f1e-ab2c-2ff7bd8409ae)

- 支持大部分常用的linux命令和参数
![11月25日(3)(2)](https://github.com/user-attachments/assets/cb1a70e0-edd9-45a9-999e-90ca8ae60c9f)

- 支持管道操作，自动补全路径，以及智能补全历史命令
![11月25日(4)](https://github.com/user-attachments/assets/3f98fa80-e495-41bd-aabc-341b5b485f9d)

# 快捷键启动
使用AutoHotKey v2工具实现快捷键启动，[AutoHotKey v2下载链接](https://www.autohotkey.com/download/ahk-v2.exe)，在任意一个文件管理器中，输入`Ctrl + T`进入命令行
![11月25日(6)](https://github.com/user-attachments/assets/9045f3f8-17e0-43c9-bd54-6fc9ff37c501)
