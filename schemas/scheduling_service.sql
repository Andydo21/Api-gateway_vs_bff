CREATE DATABASE IF NOT EXISTS scheduling_db;
USE scheduling_db;

CREATE TABLE IF NOT EXISTS `availability_templates` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `investor_id` BIGINT NOT NULL,
    `day_of_week` INT NOT NULL,
    `start_time` TIME NOT NULL,
    `end_time` TIME NOT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `pitch_slots` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `investor_id` BIGINT NOT NULL,
    `start_time` DATETIME(6) NOT NULL,
    `end_time` DATETIME(6) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'AVAILABLE',
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `scheduling_outbox_events` (
    `id?` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
