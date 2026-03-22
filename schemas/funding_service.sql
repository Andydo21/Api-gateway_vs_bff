CREATE DATABASE IF NOT EXISTS funding_db;
USE funding_db;

CREATE TABLE IF NOT EXISTS `payments` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `reference_id` BIGINT NOT NULL UNIQUE,
    `user_id` BIGINT NOT NULL,
    `amount` DECIMAL(10, 2) NOT NULL,
    `payment_method` VARCHAR(50) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `transaction_id` VARCHAR(255) NULL,
    `payment_details` JSON NOT NULL,
    `error_message` TEXT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `funding_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
