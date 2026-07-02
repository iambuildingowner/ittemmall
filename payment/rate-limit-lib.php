<?php
declare(strict_types=1);

require_once __DIR__ . '/server-config-lib.php';

function ittemmallRateLimitConfiguredPath(): string
{
    $configured = ittemmallConfigValue('ITTEMMALL_RATE_LIMIT_PATH');
    if ($configured !== '') {
        return $configured;
    }

    $orderPath = ittemmallConfigValue('ITTEMMALL_ORDER_STORE_PATH');
    if ($orderPath !== '') {
        return $orderPath . '.rate-limit.json';
    }

    $trackPath = ittemmallEffectiveTrackLogPath();
    if ($trackPath !== '') {
        return $trackPath . '.rate-limit.json';
    }

    return '';
}

function ittemmallRateLimitPathIsDerived(): bool
{
    return ittemmallConfigValue('ITTEMMALL_RATE_LIMIT_PATH') === '' && ittemmallRateLimitConfiguredPath() !== '';
}

function ittemmallRateLimitCleanScope(string $scope): string
{
    $scope = preg_replace('/[^A-Za-z0-9_.-]+/', '_', $scope) ?? 'global';
    return trim($scope, '_') !== '' ? trim($scope, '_') : 'global';
}

function ittemmallRateLimitClientHash(): string
{
    $salt = ittemmallConfigValue('ITTEMMALL_TRACK_SALT');
    if ($salt === '') {
        $salt = ittemmallEffectiveTrackSalt();
    }
    if ($salt === '') {
        $salt = ittemmallConfigValue('ITTEMMALL_ADMIN_TOKEN', 'ittemmall-rate-limit');
    }
    return hash('sha256', implode(':', [
        (string)($_SERVER['REMOTE_ADDR'] ?? ''),
        (string)($_SERVER['HTTP_USER_AGENT'] ?? ''),
        $salt,
    ]));
}

function ittemmallRateLimitEnsureDirectory(string $path): void
{
    $dir = dirname($path);
    if (!is_dir($dir) && !mkdir($dir, 0700, true)) {
        throw new RuntimeException('RATE_LIMIT_DIRECTORY_CREATE_FAILED');
    }
}

function ittemmallRateLimitRead(string $path): array
{
    if (!is_file($path)) {
        return [];
    }
    $raw = file_get_contents($path);
    if ($raw === false || trim($raw) === '') {
        return [];
    }
    $decoded = json_decode($raw, true);
    return is_array($decoded) ? $decoded : [];
}

function ittemmallRateLimitWrite(string $path, array $data): void
{
    $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    if ($json === false) {
        throw new RuntimeException('RATE_LIMIT_JSON_ENCODE_FAILED');
    }
    if (file_put_contents($path, $json, LOCK_EX) === false) {
        throw new RuntimeException('RATE_LIMIT_WRITE_FAILED');
    }
    @chmod($path, 0600);
}

function ittemmallRateLimitWithLock(callable $callback)
{
    $path = ittemmallRateLimitConfiguredPath();
    if ($path === '') {
        return $callback('');
    }

    ittemmallRateLimitEnsureDirectory($path);
    $lockPath = $path . '.lock';
    $lock = fopen($lockPath, 'c');
    if ($lock === false) {
        throw new RuntimeException('RATE_LIMIT_LOCK_OPEN_FAILED');
    }

    try {
        if (!flock($lock, LOCK_EX)) {
            throw new RuntimeException('RATE_LIMIT_LOCK_FAILED');
        }
        return $callback($path);
    } finally {
        flock($lock, LOCK_UN);
        fclose($lock);
        @chmod($lockPath, 0600);
    }
}

function ittemmallRateLimitCheck(string $scope, int $maxRequests, int $windowSeconds): array
{
    $path = ittemmallRateLimitConfiguredPath();
    $scope = ittemmallRateLimitCleanScope($scope);
    $maxRequests = max(1, $maxRequests);
    $windowSeconds = max(1, $windowSeconds);
    if ($path === '') {
        return [
            'allowed' => true,
            'configured' => false,
            'scope' => $scope,
            'limit' => $maxRequests,
            'remaining' => $maxRequests,
            'retryAfter' => 0,
        ];
    }

    return ittemmallRateLimitWithLock(static function (string $lockedPath) use ($scope, $maxRequests, $windowSeconds): array {
        $now = time();
        $cutoff = $now - $windowSeconds;
        $key = $scope . ':' . ittemmallRateLimitClientHash();
        $data = ittemmallRateLimitRead($lockedPath);
        $next = [];

        foreach ($data as $entryKey => $timestamps) {
            if (!is_array($timestamps)) {
                continue;
            }
            $recent = array_values(array_filter(array_map('intval', $timestamps), static function (int $timestamp) use ($cutoff): bool {
                return $timestamp > $cutoff;
            }));
            if ($recent !== []) {
                $next[(string)$entryKey] = $recent;
            }
        }

        $hits = $next[$key] ?? [];
        if (count($hits) >= $maxRequests) {
            ittemmallRateLimitWrite($lockedPath, $next);
            $oldest = min($hits);
            return [
                'allowed' => false,
                'configured' => true,
                'scope' => $scope,
                'limit' => $maxRequests,
                'remaining' => 0,
                'retryAfter' => max(1, $windowSeconds - ($now - $oldest)),
            ];
        }

        $hits[] = $now;
        $next[$key] = $hits;
        if (count($next) > 2000) {
            uasort($next, static function (array $a, array $b): int {
                return max($b) <=> max($a);
            });
            $next = array_slice($next, 0, 2000, true);
        }
        ittemmallRateLimitWrite($lockedPath, $next);

        return [
            'allowed' => true,
            'configured' => true,
            'scope' => $scope,
            'limit' => $maxRequests,
            'remaining' => max(0, $maxRequests - count($hits)),
            'retryAfter' => 0,
        ];
    });
}

function ittemmallRateLimitInspect(): array
{
    $path = ittemmallRateLimitConfiguredPath();
    $configured = $path !== '';
    $dir = $configured ? dirname($path) : '';
    $fileExists = $configured && is_file($path);
    $validJson = null;
    $entryCount = 0;

    if ($fileExists) {
        $raw = file_get_contents($path);
        $decoded = $raw === false ? null : json_decode((string)$raw, true);
        $validJson = is_array($decoded);
        $entryCount = is_array($decoded) ? count($decoded) : 0;
    }

    $lockPath = $configured ? $path . '.lock' : '';
    $lockExists = $lockPath !== '' && is_file($lockPath);

    return [
        'configured' => $configured,
        'derivedFromPrivatePath' => ittemmallRateLimitPathIsDerived(),
        'directoryExists' => $dir !== '' && is_dir($dir),
        'directoryWritable' => $dir !== '' && is_dir($dir) && is_writable($dir),
        'fileExists' => $fileExists,
        'fileReadable' => $fileExists && is_readable($path),
        'fileValidJson' => $validJson,
        'entryCount' => $entryCount,
        'lockFileExists' => $lockExists,
        'lockWritable' => $lockExists ? is_writable($lockPath) : ($dir !== '' && is_dir($dir) && is_writable($dir)),
    ];
}
