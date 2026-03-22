CREATE DATABASE IF NOT EXISTS notification_db;
USE notification_db;

CREATE TABLE IF NOT EXISTS `notifications` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `message` TEXT NOT NULL,
    `notification_type` VARCHAR(20) NOT NULL DEFAULT 'info',
    `is_read` BOOLEAN NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
