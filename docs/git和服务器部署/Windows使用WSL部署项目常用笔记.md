WSL：Windows Subsystem for Linux（简称WSL）是一个在Windows 10\11上能够运行原生Linux二进制 可执行文件（ ELF格式）的兼容层。它是由 微软与 Canonical公司合作开发，开发人员可以在 Windows 计算机上同时访问 Windows 和 Linux 的强大功能。 通过适用于 Linux 的 Windows 子系统 (WSL)，开发人员可以安装 Linux 发行版（例如 Ubuntu、 OpenSUSE、 Kali、 Debian、 Arch Linux 等），并直接在 Windows 上使用 Linux 应用程序、实用程序和 Bash 命令行工具，不用进行任何修改，也无需承担传统虚拟机或双启动设置的费用。
Windows 使用 WSL 部署项目常用笔记
1. 前置说明本文使用 
<服务器IP> 作为占位符，执行命令前替换为实际服务器地址。Windows 磁盘在 WSL 中的映射关系：
text
D:\tianwen_project\GitHub_project\qixiang_tools
↓
/mnt/d/tianwen_project/GitHub_project/qixiang_tools


⚠️ 重要规则：所有 rsync 命令必须先进入 WSL Ubuntu 终端再执行，禁止直接粘贴到 PowerShell，否则续行符、--exclude 参数会解析异常。

2. WSL 一次性安装（修正旧文档坑点）
以管理员 PowerShell 执行（推荐指定稳定版本，避免滚动版初始化失败）：
powershell
wsl --install --web-download -d Ubuntu-24.04


新增 --web-download：绕过微软商店下载异常、403、下载完成无法注册分发的问题。

✅ 关键操作顺序（旧文档漏洞修复）
1.等待下载、自动启动 Ubuntu 实例
2.在弹出的 Ubuntu 终端内创建 Linux 用户名、密码（必须走完这一步！）
3.账户初始化完成后，再重启 Windows（不要下载完直接重启）
重启后 PowerShell 直接输入即可进入默认 Ubuntu：
powershell
wsl

首次进入 Ubuntu 设置用户名密码：输入密码时终端不显示字符，属于正常现象。
进入 Ubuntu，安装部署必备工具：
bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y rsync openssh-client
rsync --version
ssh -V


踩坑说明：安装 WSL 出现 403 时，通常是代理拦截 Microsoft 下载源，关闭代理或切换网络重试。

可选优化（安装完成后执行，统一默认发行版）
新开 PowerShell 执行：
powershell
wsl -l -v
wsl --set-default Ubuntu-24.04

3. 部署前准备
1.如果修改前端代码，在 Windows PowerShell 执行打包
powershell
cd D:\tianwen_project\GitHub_project\qixiang_tools\frontend
npm run build

看到 
built 代表打包成功；体积警告仅为提示，不影响部署。
1.进入 WSL 并切换到项目根目录
powershell
wsl

bash
cd /mnt/d/tianwen_project/GitHub_project/qixiang_tools

4. 首次先预演（强烈建议每次同步前执行）首次部署、调整排除规则、更新同步规则后，必须先用 
--dry-run。仅打印变更清单，不会真实上传 / 删除服务器文件，规避误删风险。
bash
rsync -az --dry-run --delete --itemize-changes \
  --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r \
  --exclude .git/ \
  --exclude backend/.venv/ \
  --exclude backend/.server-venv/ \
  --exclude frontend/node_modules/ \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude .DS_Store \
  --exclude '._*' \
  --exclude .env \
  --exclude backend/.env \
  --exclude 'backend/.mysql-*' \
  --exclude uploads/ \
  --exclude logs/ \
  --exclude '*.sqlite3' \
  --exclude '*.db' \
  --exclude .idea/ \
  --exclude .vscode/ \
  --exclude .venv/ \
  --exclude .pytest_cache/ \
  --exclude backend/app/temp/ \
  --exclude frontend/test-results/ \
  --exclude log/ \
  --exclude '*.log' \
  --exclude .env.local \
  --exclude '*.sqlite' \
  -e "ssh -o StrictHostKeyChecking=accept-new" \
  ./ \
  ubuntu@<服务器IP>:/home/ubuntu/qixiang_tools/


修改点：将 **pycache**/ 修正为标准匹配 __pycache__/，旧写法匹配失效。

预演重点核查：服务器以下目录 / 文件不会被删除、覆盖
- backend/.env（服务环境变量，严禁覆盖）
- backend/.server-venv/（服务器独立虚拟环境）
- sqlite/sqlite3 数据库文件
- uploads/、log/、logs/ 用户上传文件与运行日志
- backend/app/temp/ 临时目录
5. 正式同步确认 dry-run 输出清单无风险后，删除参数 
--dry-run，其余参数完全不变：
bash
rsync -az --delete --itemize-changes \
  --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r \
  --exclude .git/ \
  --exclude backend/.venv/ \
  --exclude backend/.server-venv/ \
  --exclude frontend/node_modules/ \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude .DS_Store \
  --exclude '._*' \
  --exclude .env \
  --exclude backend/.env \
  --exclude 'backend/.mysql-*' \
  --exclude uploads/ \
  --exclude logs/ \
  --exclude '*.sqlite3' \
  --exclude '*.db' \
  --exclude .idea/ \
  --exclude .vscode/ \
  --exclude .venv/ \
  --exclude .pytest_cache/ \
  --exclude backend/app/temp/ \
  --exclude frontend/test-results/ \
  --exclude log/ \
  --exclude '*.log' \
  --exclude .env.local \
  --exclude '*.sqlite' \
  -e "ssh -o StrictHostKeyChecking=accept-new" \
  ./ \
  ubuntu@<服务器IP>:/home/ubuntu/qixiang_tools/


关键提醒：源目录 ./ 尾部斜杠不能省略；代表同步目录内全部内容，不会在服务器嵌套一层项目文件夹。

6. 服务器更新操作
文件同步完成后登录服务器：
bash
ssh ubuntu@<服务器IP>
cd /home/ubuntu/qixiang_tools

1.修改 Python 依赖包时执行：
bash
./backend/.server-venv/bin/python -m pip install -r backend/requirements.txt

1.修改后端代码、调整配置文件、更新依赖后重启服务：
bash
sudo systemctl restart qixiang-backend
sudo systemctl status qixiang-backend --no-pager
curl -s http://127.0.0.1:8000/api/health

# 如果有修改外部依赖，需要在服务器更新同步哦，本项目详细外部依赖请参考文档：后端依赖库外部依赖说明

1.仅改动前端：frontend/dist 同步完成后 Nginx 一般即时生效，浏览器使用 Ctrl+F5 硬刷新清除缓存。
7. 常见问题（新增大量踩坑点）
7.1 rsync 参数异常、排除规则失效现象：
--exclude 不生效、多行命令报错✅ 原因：命令直接粘贴进 PowerShell；PowerShell 不识别 
\ 换行续行符✅ 解决方案：先执行 wsl 进入 Ubuntu 终端，再粘贴整条 rsync 命令
7.2 rsync: command not found
bash
sudo apt update
sudo apt install -y rsync

7.3 SSH 主机指纹报错当前参数 
StrictHostKeyChecking=accept-new 自动信任全新服务器指纹；如果服务器重装、IP 复用导致指纹变更，会主动拒绝连接。解决：本地 WSL 删除旧主机记录
bash
ssh-keygen -R <服务器IP>

然后重新执行 rsync，确认新的指纹后输入 `yes`。

### 7.4 后端接口没有更新

```bash
sudo systemctl restart qixiang-backend
sudo journalctl -u qixiang-backend -n 80 --no-pager
```

### 7.5 前端页面还是旧版本

1. 确认 Windows 本地已经执行 `npm run build`，生成最新 `dist`
2. 确认 rsync 没有排除 `frontend/dist/`
3. 浏览器 `Ctrl+F5` 硬刷新；必要时清除浏览器缓存

7.6 WSL 安装成功，但是 wsl -l -v 看不到分发根源：下载完成直接重启，没有走完 Ubuntu 初始化账户流程。解决：使用 
wsl --install --web-download -d Ubuntu-24.04 重装，等待自动弹出 Ubuntu 窗口创建账号后再重启电脑。
7.7 WSL 访问 Windows 项目读写慢项目路径 
/mnt/d/ 属于 Windows 跨磁盘挂载，IO 性能偏弱；频繁编译开发建议把项目复制到 WSL 内部目录 
~/qixiang_tools/ 开发。
7.8 rsync --delete 误删服务器文件⚠️ 严禁跳过 
--dry-run 直接同步；务必核对预演输出，确认服务器持久目录（uploads、env、虚拟环境）全部被 exclude。
可选小工具（附加）
如需关闭运行中的 WSL 虚拟机：
powershell
wsl --shutdown
