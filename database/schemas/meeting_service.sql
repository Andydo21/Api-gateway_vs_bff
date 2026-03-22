CREATE DATABASE IF NOT EXISTS meeting_db;
USE meeting_db;

CREATE TABLE IF NOT EXISTS `meetings` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `booking_id` BIGINT NOT NULL,
    `meeting_url` VARCHAR(500) NOT NULL,
    `meeting_type` VARCHAR(50) NOT NULL,
    `start_time` DATETIME(6) NOT NULL,
    `end_time` DATETIME(6) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'ONGOING',
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `meeting_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
