<?php
declare(strict_types=1);

function ittemmallServerConfigDefaultPath(): string
{
    return dirname(__DIR__, 2) . '/ittemmall-private/ittemmall-server-config.php';
}

function ittemmallServerConfigCandidatePaths(): array
{
    $paths = [];
    $envPath = getenv('ITTEMMALL_SERVER_CONFIG_PATH');
    if ($envPath !== false && trim((string)$envPath) !== '') {
        $paths[] = trim((string)$envPath);
    }

    $paths[] = ittemmallServerConfigDefaultPath();
    $paths[] = dirname(__DIR__) . '/ittemmall-private/ittemmall-server-config.php';

    $documentRoot = $_SERVER['DOCUMENT_ROOT'] ?? '';
    if (is_string($documentRoot) && trim($documentRoot) !== '') {
        $root = rtrim(trim($documentRoot), '/');
        $paths[] = $root . '/../ittemmall-private/ittemmall-server-config.php';
        $paths[] = $root . '/ittemmall-private/ittemmall-server-config.php';
    }

    return array_values(array_unique($paths));
}

function ittemmallDefaultPrivateDir(): string
{
    return dirname(__DIR__, 2) . '/ittemmall-private';
}

function ittemmallKstDate(): string
{
    return (new DateTimeImmutable('now', new DateTimeZone('Asia/Seoul')))->format('Y-m-d');
}

function ittemmallEffectiveTrackLogPath(?string $date = null): string
{
    $date = $date ?: ittemmallKstDate();
    $configured = ittemmallConfigValue('ITTEMMALL_TRACK_LOG_PATH');
    if ($configured !== '') {
        if (str_contains($configured, '{date}')) {
            return str_replace('{date}', $date, $configured);
        }
        if (str_ends_with($configured, '/') || is_dir($configured)) {
            return rtrim($configured, '/') . '/' . $date . '.ndjson';
        }
        return $configured;
    }
    return ittemmallDefaultPrivateDir() . '/data/pixel-events/' . $date . '.ndjson';
}

function ittemmallTrackSaltPath(): string
{
    return ittemmallDefaultPrivateDir() . '/track-salt.txt';
}

function ittemmallEffectiveTrackSalt(): string
{
    $configured = ittemmallConfigValue('ITTEMMALL_TRACK_SALT');
    if ($configured !== '') {
        return $configured;
    }

    $saltPath = ittemmallTrackSaltPath();
    if (is_file($saltPath)) {
        $salt = trim((string)file_get_contents($saltPath));
        if ($salt !== '') {
            return $salt;
        }
    }

    $dir = dirname($saltPath);
    if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
        return '';
    }

    $salt = bin2hex(random_bytes(32));
    if (file_put_contents($saltPath, $salt . PHP_EOL, LOCK_EX) === false) {
        return '';
    }
    @chmod($saltPath, 0600);
    return $salt;
}

function ittemmallServerConfigPath(): string
{
    foreach (ittemmallServerConfigCandidatePaths() as $path) {
        if (is_file($path)) {
            return $path;
        }
    }
    return ittemmallServerConfigDefaultPath();
}

function ittemmallServerConfig(): array
{
    static $config = null;
    if ($config !== null) {
        return $config;
    }

    $path = ittemmallServerConfigPath();
    if (!is_file($path)) {
        $config = [];
        return $config;
    }

    $loaded = require $path;
    $config = is_array($loaded) ? $loaded : [];
    return $config;
}

function ittemmallServerConfigFileLoaded(): bool
{
    return is_file(ittemmallServerConfigPath()) && ittemmallServerConfig() !== [];
}

function ittemmallConfigValue(string $key, string $default = ''): string
{
    $envValue = getenv($key);
    if ($envValue !== false && trim((string)$envValue) !== '') {
        return trim((string)$envValue);
    }

    $config = ittemmallServerConfig();
    if (!array_key_exists($key, $config)) {
        return $default;
    }

    $value = $config[$key];
    if (is_bool($value)) {
        return $value ? '1' : '0';
    }
    if (is_scalar($value)) {
        return trim((string)$value);
    }
    return $default;
}

function ittemmallConfigPresent(string $key): bool
{
    return ittemmallConfigValue($key) !== '';
}
