<?php
declare(strict_types=1);

require_once __DIR__ . '/order-store-lib.php';
require_once __DIR__ . '/rate-limit-lib.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function ittemmallHealthEnvPresent(string $key): bool
{
    return ittemmallConfigPresent($key);
}

function ittemmallHealthPublicConfigValue(string $text, string $key): string
{
    $pattern = '/\b' . preg_quote($key, '/') . '\s*:\s*([\'"])(.*?)\1/s';
    if (!preg_match($pattern, $text, $matches)) {
        return '';
    }
    return trim((string)$matches[2]);
}

function ittemmallHealthLooksPlaceholder(string $value): bool
{
    $value = strtoupper($value);
    foreach (['YOUR_', 'PUBLIC_', 'NAVER_PAY_', 'ISSUED_', 'ISSUED-', 'TEST_', 'REPLACE-WITH'] as $marker) {
        if (strpos($value, $marker) !== false) {
            return true;
        }
    }
    return false;
}

function ittemmallHealthInspectOrderJson(string $path): array
{
    $result = [
        'exists' => is_file($path),
        'readable' => false,
        'validJson' => null,
        'orderCount' => 0,
        'latestUpdatedAt' => '',
    ];

    if (!$result['exists']) {
        return $result;
    }

    $result['readable'] = is_readable($path);
    if (!$result['readable']) {
        $result['validJson'] = false;
        return $result;
    }

    $raw = file_get_contents($path);
    if ($raw === false) {
        $result['validJson'] = false;
        return $result;
    }

    if (trim($raw) === '') {
        $result['validJson'] = true;
        return $result;
    }

    $decoded = json_decode($raw, true);
    if (!is_array($decoded)) {
        $result['validJson'] = false;
        return $result;
    }

    $orders = array_values(array_filter($decoded, 'is_array'));
    $result['validJson'] = true;
    $result['orderCount'] = count($orders);
    foreach ($orders as $order) {
        $updatedAt = (string)($order['updatedAt'] ?? $order['createdAt'] ?? '');
        if ($updatedAt !== '' && strcmp($updatedAt, (string)$result['latestUpdatedAt']) > 0) {
            $result['latestUpdatedAt'] = $updatedAt;
        }
    }
    return $result;
}

$orderPath = ittemmallOrderStorePath();
$orderDir = $orderPath === '' ? '' : dirname($orderPath);
$curlReady = function_exists('curl_init');
$jsonReady = function_exists('json_encode') && function_exists('json_decode');
$orderStoreConfigured = $orderPath !== '';
$orderStoreDirectoryExists = $orderDir !== '' && is_dir($orderDir);
$orderStoreDirectoryWritable = $orderStoreDirectoryExists && is_writable($orderDir);
$orderJson = $orderPath !== '' ? ittemmallHealthInspectOrderJson($orderPath) : [
    'exists' => false,
    'readable' => false,
    'validJson' => null,
    'orderCount' => 0,
    'latestUpdatedAt' => '',
];
$orderBackupJson = $orderPath !== '' ? ittemmallHealthInspectOrderJson($orderPath . '.bak') : [
    'exists' => false,
    'readable' => false,
    'validJson' => null,
    'orderCount' => 0,
    'latestUpdatedAt' => '',
];
$orderLockPath = ittemmallOrderStoreLockPath();
$orderLockExists = $orderLockPath !== '' && is_file($orderLockPath);
$orderLockWritable = $orderLockExists ? is_writable($orderLockPath) : $orderStoreDirectoryWritable;
$rateLimit = ittemmallRateLimitInspect();
$mailReady = function_exists('mail');
$clientId = ittemmallConfigValue('NAVER_PAY_CLIENT_ID');
$clientSecret = ittemmallConfigValue('NAVER_PAY_CLIENT_SECRET');
$chainId = ittemmallConfigValue('NAVER_PAY_CHAIN_ID');
$mode = ittemmallConfigValue('NAVER_PAY_MODE', 'development');
$clientIdConfigured = $clientId !== '' && !ittemmallHealthLooksPlaceholder($clientId);
$clientSecretConfigured = $clientSecret !== '' && !ittemmallHealthLooksPlaceholder($clientSecret);
$chainIdConfigured = $chainId !== '' && !ittemmallHealthLooksPlaceholder($chainId);
$approveUrlOverride = ittemmallConfigValue('NAVER_PAY_APPROVE_URL');
$approveUrlLooksHttps = $approveUrlOverride === '' || stripos($approveUrlOverride, 'https://') === 0;
$cancelUrlOverride = ittemmallConfigValue('NAVER_PAY_CANCEL_URL');
$cancelUrlLooksHttps = $cancelUrlOverride === '' || stripos($cancelUrlOverride, 'https://') === 0;
$adminTokenConfigured = ittemmallHealthEnvPresent('ITTEMMALL_ADMIN_TOKEN');
$notifyEmail = ittemmallConfigValue('ITTEMMALL_NOTIFY_EMAIL');
$notifyFrom = ittemmallConfigValue('ITTEMMALL_NOTIFY_FROM', 'no-reply@ittemmall.com');
$publicConfigPath = __DIR__ . '/naverpay-config.js';
$publicConfigReadable = is_file($publicConfigPath);
$publicConfigText = $publicConfigReadable ? (string)file_get_contents($publicConfigPath) : '';
$publicClientId = ittemmallHealthPublicConfigValue($publicConfigText, 'clientId');
$publicChainId = ittemmallHealthPublicConfigValue($publicConfigText, 'chainId');
$publicMode = ittemmallHealthPublicConfigValue($publicConfigText, 'mode');
$publicClientIdConfigured = $publicClientId !== '' && !ittemmallHealthLooksPlaceholder($publicClientId);
$publicChainIdConfigured = $publicChainId !== '' && !ittemmallHealthLooksPlaceholder($publicChainId);
$publicModeConfigured = in_array($publicMode, ['development', 'production'], true);
$publicClientSecretExposed = stripos($publicConfigText, 'clientSecret') !== false || strpos($publicConfigText, 'CLIENT_SECRET') !== false;
$publicModeMatchesServer = $publicModeConfigured && $publicMode === $mode;
$publicClientIdMatchesServer = $publicClientIdConfigured && $clientIdConfigured && hash_equals($clientId, $publicClientId);
$publicChainIdMatchesServer = $publicChainIdConfigured && $chainIdConfigured && hash_equals($chainId, $publicChainId);

$missingForApproval = [];
if (!$curlReady) {
    $missingForApproval[] = 'php.curl';
}
if (!$jsonReady) {
    $missingForApproval[] = 'php.json';
}
if (!$orderStoreConfigured) {
    $missingForApproval[] = 'ITTEMMALL_ORDER_STORE_PATH';
}
if (!$orderStoreDirectoryWritable) {
    $missingForApproval[] = 'serverOrderStore.directoryWritable';
}
if ($orderJson['exists'] && !$orderJson['validJson']) {
    $missingForApproval[] = 'serverOrderStore.validJson';
}
if ($orderLockExists && !$orderLockWritable) {
    $missingForApproval[] = 'serverOrderStore.lockWritable';
}
if ($rateLimit['configured'] && !$rateLimit['directoryWritable']) {
    $missingForApproval[] = 'rateLimit.directoryWritable';
}
if ($rateLimit['configured'] && $rateLimit['lockFileExists'] && !$rateLimit['lockWritable']) {
    $missingForApproval[] = 'rateLimit.lockWritable';
}
if (!$clientIdConfigured) {
    $missingForApproval[] = 'NAVER_PAY_CLIENT_ID';
}
if (!$clientSecretConfigured) {
    $missingForApproval[] = 'NAVER_PAY_CLIENT_SECRET';
}
if (!$chainIdConfigured) {
    $missingForApproval[] = 'NAVER_PAY_CHAIN_ID';
}
if (!$approveUrlLooksHttps) {
    $missingForApproval[] = 'NAVER_PAY_APPROVE_URL_HTTPS';
}
if (!$publicConfigReadable) {
    $missingForApproval[] = 'publicNaverPay.configFile';
}
if ($publicClientSecretExposed) {
    $missingForApproval[] = 'publicNaverPay.noClientSecret';
}
if (!$publicClientIdConfigured) {
    $missingForApproval[] = 'publicNaverPay.clientId';
}
if (!$publicChainIdConfigured) {
    $missingForApproval[] = 'publicNaverPay.chainId';
}
if (!$publicModeMatchesServer) {
    $missingForApproval[] = 'publicNaverPay.modeMatchesServer';
}
if ($publicClientIdConfigured && $clientIdConfigured && !$publicClientIdMatchesServer) {
    $missingForApproval[] = 'publicNaverPay.clientIdMatchesServer';
}
if ($publicChainIdConfigured && $chainIdConfigured && !$publicChainIdMatchesServer) {
    $missingForApproval[] = 'publicNaverPay.chainIdMatchesServer';
}

$missingForOperations = $missingForApproval;
if (!$adminTokenConfigured) {
    $missingForOperations[] = 'ITTEMMALL_ADMIN_TOKEN';
}
if (!$cancelUrlLooksHttps) {
    $missingForOperations[] = 'NAVER_PAY_CANCEL_URL_HTTPS';
}

echo json_encode([
    'ok' => true,
    'site' => 'ITTEMMALL',
    'php' => [
        'version' => PHP_VERSION,
        'curl' => $curlReady,
        'json' => $jsonReady,
        'mail' => $mailReady,
    ],
    'serverConfig' => [
        'privateConfigFileLoaded' => ittemmallServerConfigFileLoaded(),
    ],
    'serverOrderStore' => [
        'configured' => $orderStoreConfigured,
        'directoryExists' => $orderStoreDirectoryExists,
        'directoryWritable' => $orderStoreDirectoryWritable,
        'fileExists' => $orderJson['exists'],
        'fileReadable' => $orderJson['readable'],
        'fileValidJson' => $orderJson['validJson'],
        'orderCount' => $orderJson['orderCount'],
        'latestUpdatedAt' => $orderJson['latestUpdatedAt'],
        'backupExists' => $orderBackupJson['exists'],
        'backupReadable' => $orderBackupJson['readable'],
        'backupValidJson' => $orderBackupJson['validJson'],
        'backupOrderCount' => $orderBackupJson['orderCount'],
        'backupLatestUpdatedAt' => $orderBackupJson['latestUpdatedAt'],
        'lockFileExists' => $orderLockExists,
        'lockWritable' => $orderLockWritable,
    ],
    'naverPay' => [
        'mode' => $mode,
        'clientIdConfigured' => $clientIdConfigured,
        'clientSecretConfigured' => $clientSecretConfigured,
        'chainIdConfigured' => $chainIdConfigured,
        'approveUrlOverrideConfigured' => $approveUrlOverride !== '',
        'approveUrlLooksHttps' => $approveUrlLooksHttps,
        'approvalEnabled' => ittemmallConfigValue('NAVER_PAY_APPROVE_ENABLED') === '1',
        'cancelUrlOverrideConfigured' => $cancelUrlOverride !== '',
        'cancelUrlLooksHttps' => $cancelUrlLooksHttps,
        'cancelEnabled' => ittemmallConfigValue('NAVER_PAY_CANCEL_ENABLED') === '1',
    ],
    'publicNaverPay' => [
        'configFileExists' => $publicConfigReadable,
        'mode' => $publicMode,
        'modeConfigured' => $publicModeConfigured,
        'clientIdConfigured' => $publicClientIdConfigured,
        'chainIdConfigured' => $publicChainIdConfigured,
        'clientSecretExposed' => $publicClientSecretExposed,
        'modeMatchesServer' => $publicModeMatchesServer,
        'clientIdMatchesServer' => $publicClientIdMatchesServer,
        'chainIdMatchesServer' => $publicChainIdMatchesServer,
    ],
    'tracking' => [
        'logPathConfigured' => ittemmallHealthEnvPresent('ITTEMMALL_TRACK_LOG_PATH'),
        'saltConfigured' => ittemmallHealthEnvPresent('ITTEMMALL_TRACK_SALT'),
    ],
    'rateLimit' => $rateLimit,
    'admin' => [
        'adminTokenConfigured' => $adminTokenConfigured,
    ],
    'notification' => [
        'enabled' => ittemmallConfigValue('ITTEMMALL_NOTIFY_ENABLED') === '1',
        'recipientConfigured' => $notifyEmail !== '',
        'recipientLooksValid' => $notifyEmail !== '' && filter_var($notifyEmail, FILTER_VALIDATE_EMAIL) !== false,
        'fromConfigured' => $notifyFrom !== '',
        'fromLooksValid' => $notifyFrom !== '' && filter_var($notifyFrom, FILTER_VALIDATE_EMAIL) !== false,
        'mailFunctionAvailable' => $mailReady,
    ],
    'readiness' => [
        'readyToEnableNaverPayApproval' => $missingForApproval === [],
        'readyForOrderOperations' => $missingForOperations === [],
        'missingForApproval' => $missingForApproval,
        'missingForOperations' => $missingForOperations,
    ],
], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
