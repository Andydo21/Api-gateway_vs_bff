CREATE DATABASE IF NOT EXISTS resource_db;
USE resource_db;

CREATE TABLE IF NOT EXISTS `event_resources` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `startup_id` BIGINT NOT NULL UNIQUE,
    `startup_name` VARCHAR(255) NOT NULL,
    `available_quantity` INT NOT NULL DEFAULT 0,
    `reserved_quantity` INT NOT NULL DEFAULT 0,
    `reorder_level` INT NOT NULL DEFAULT 10,
    `last_restocked` DATETIME(6) NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at?` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `resource_reservations` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `resource_id` BIGINT NOT NULL,
    `booking_id` BIGINT NOT NULL,
    `quantity` INT NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'active',
    `expires_at` DATETIME(6) NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    FOREIGN KEY (`resource_id`) REFERENCES `event_resources`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `resource_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
