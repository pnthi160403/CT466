<?php

require_once __DIR__ . '/../vendor/autoload.php';

define("BASE_URI", "http://localhost:8080");
define("API_TEXTSUM_VI_LANG", "http://127.0.0.1:8000/vi_lang");
define("API_TEXTSUM_EN_LANG", "http://127.0.0.1:8000/en_lang");
define("API_INIT_VI_LANG", "http://127.0.0.1:8000/init_vi_lang");
define("API_INIT_EN_LANG", "http://127.0.0.1:8000/init_en_lang");

function dd($data) {
    echo '<pre>';
    var_dump($data);
    echo '</pre>';
    exit;
}

function callApi($content, $apiUrl) {
    $client = new \GuzzleHttp\Client();
    try {
        $response = $client->post($apiUrl, [
            'json' => ['src' => $content]
        ]);
        $result = json_decode($response->getBody()->getContents(), true);
        return $result;
    } catch (\GuzzleHttp\Exception\RequestException $e) {
        return ['error' => 'Không thể kết nối với API: ' . $e->getMessage()];
    }
}

$result = null;
$lang =  "";

if (isset($_GET['en'])) {
    $lang = 'en';
    callApi('', API_INIT_EN_LANG);
} elseif (isset($_GET['vi'])) {
    $lang = 'vi';
    callApi('', API_INIT_VI_LANG);
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $content = $_POST['content'];
    $result = callApi($content, $lang == 'en' ? API_TEXTSUM_EN_LANG : API_TEXTSUM_VI_LANG);
}

?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Ứng dụng tóm tắt văn bản</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css" integrity="sha512-z3gLpd7yknf1YoNbCzqRKc4qyor8gaKU1qmn+CShxbuBusANI9QpRohGBreCFkKxLhei6S9CQXFEbbKuqLg0DA==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <link href="/css/style.css" rel="stylesheet">
</head>

<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Ứng dụng tóm tắt văn bản</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="?vi">Tóm tắt văn bản tiếng Việt</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="?en">Tóm tắt văn bản tiếng Anh</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <?php if (empty($lang)): ?>
        <h2 class="text-center">Xin chào!</h2>
    <?php else: ?>
        <h2 class="text-center">
            <?php if ($lang == 'en'): ?>
                Tóm tắt văn bản tiếng Anh
            <?php else: ?>
                Tóm tắt văn bản tiếng Việt
            <?php endif; ?>
        </h2>
    
        <div class="container">
        <form action="" method="post">
            <div class="mb-4">
                <label for="content" class="form-label">Nhập văn bản</label>
                <textarea name="content" id="content" class="form-control" placeholder="Nhập văn bản bạn muốn tóm tắt..." required><?php echo isset($content) ? htmlspecialchars($content) : ''; ?></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Tóm tắt</button>
        </form>

        <?php if ($result): ?>
            <div class="result-box">
                <h2>Kết quả tóm tắt:</h2>
                <?php if (isset($result['error'])): ?>
                    <p class="error-message"><?php echo $result['error']; ?></p>
                <?php elseif (isset($result['result'])): ?>
                    <p><?php echo nl2br(htmlspecialchars($result['result'])); ?></p>
                <?php endif; ?>
            </div>
            <?php endif; ?>
        </div>
    <?php endif; ?>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM"
        crossorigin="anonymous"></script>
</body>

</html>