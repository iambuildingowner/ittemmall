<?php
declare(strict_types=1);

function ittemmallServerConfigDefaultPath(): string
{
    return dirname(__DIR__, 2) . '/ittemmall-private/ittemmall-server-config.php';
}

function ittemmallServerConfigPath(): string
{
    $path = getenv('ITTEMMALL_SERVER_CONFIG_PATH');
    if ($path !== false && trim((string)$path) !== '') {
        return trim((string)$path);
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
