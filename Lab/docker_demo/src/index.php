<?php
$host = 'localhost';
$username = 'root';
$password = '123456';
$database = 'ctf';


$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    die("连接失败: " . $conn->connect_error);
}

$query = '';
$resultText = '';

if ($_SERVER["REQUEST_METHOD"] == "GET" && isset($_GET['user'])) {
    $userInput = $_GET['user'];
    $query = "SELECT username,password FROM users WHERE id = '$userInput'";

    $result = $conn->query($query);
    if ($result) { 
        $rows = mysqli_fetch_all($result, MYSQLI_ASSOC);
        $resultText = $result->num_rows > 0 ? implode(", ", array_map('implode', array_fill(0, count($rows), ', '), $rows)) : '无结果 😶';
        $result->close();
    } else {
        $resultText = "查询错误: " . $conn->error . " 😵";
    }
}

$conn->close();
?>

<!DOCTYPE html>
<html lang="zh">

<head>
    <meta charset="UTF-8">
    <title>SQL 注入教学局 🕵️‍♂️</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/atom-one-dark.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js"></script>
    <script>
        hljs.initHighlightingOnLoad();
    </script>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #282c34;
            color: #abb2bf;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 700px;
            margin: 20px auto;
            background: #21252b;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }

        h1 {
            color: #61afef;
            text-align: center;
        }

        form {
            margin-bottom: 20px;
            text-align: center;
        }

        input[type="text"] {
            width: 70%;
            padding: 8px;
            margin-top: 10px;
            border: 1px solid #181a1f;
            border-radius: 4px;
            background: #1c1e24;
            color: #abb2bf;
            font-size: 1rem;
        }

        input[type="submit"] {
            padding: 8px 16px;
            margin-top: 10px;
            border: none;
            border-radius: 4px;
            background-color: #61afef;
            color: white;
            cursor: pointer;
            font-size: 1rem;
        }

        input[type="submit"]:hover {
            background-color: #528bff;
        }

        pre code {
            font-family: 'Roboto Mono', monospace;
            /* 平滑等宽字体 */
            font-size: 1rem;
        }

        .sql-display,
        .result {
            background-color: #282c34;
            color: #abb2bf;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 0.95rem;
            border: 1px solid #181a1f;
        }
    </style>
</head>

<body>

    <div class="container">
        <h1>SQL 注入教学局 🕵️‍♂️</h1>
        <pre><code id="sqlStatement" class="sql hljs">SELECT username,password FROM users WHERE id= ''</code></pre>
        <form method="get">
            <label for="user">请输入用户名 🔍:</label><br>
            <input type="text" id="user" name="user" oninput="updateSQLStatement()" required>
            <input type="submit" value="执行查询 🚀">
        </form>
        <?php if ($_SERVER["REQUEST_METHOD"] == "GET" && isset($_GET['user'])) : ?>
            <div class='sql-display'>拼接后的 SQL 语句 👀:</div>
            <pre><code><?= htmlspecialchars($query) ?></code></pre>
            <div class='result'>查询结果: <?= htmlspecialchars($resultText) ?></div>
        <?php endif; ?>
    </div>

    <div class="container">
        <h2>后端 SQL 逻辑展示 🧠</h2>
        <pre><code class="php hljs">
function waf(){
    ...
}
if ($_SERVER["REQUEST_METHOD"] == "GET" && isset($_GET['user'])) {
    $userInput = waf($_GET['user']);
    $query = "SELECT username,password FROM users WHERE id= '$userInput'";
    $result = $conn->query($query);
    if ($result) {
        ...
    } else {
        ...
    }
}
$conn->close();
    </code></pre>
    </div>
    <script>
        function updateSQLStatement() {
            var userValue = document.getElementById('user').value.replace(/</g, "&lt;").replace(/>/g, "&gt;");
            var sqlStatementElement = document.getElementById('sqlStatement');
            sqlStatementElement.textContent = "SELECT username,password FROM users WHERE id= '" + userValue + "'";
            hljs.highlightElement(sqlStatementElement);
        }
    </script>
</body>

</html>