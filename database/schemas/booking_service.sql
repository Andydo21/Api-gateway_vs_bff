CREATE DATABASE IF NOT EXISTS booking_db;
USE booking_db;

CREATE TABLE IF NOT EXISTS `pitch_requests` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `startup_id` BIGINT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `pitch_deck_url` VARCHAR(500) NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'REGISTERED',
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `pitch_bookings` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `pitch_request_id` BIGINT NOT NULL,
    `pitch_slot_id` BIGINT NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED',
    `created_at` DATETIME(6) NOT NULL,
    FOREIGN KEY (`pitch_request_id`) REFERENCES `pitch_requests`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `waitlists` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `pitch_request_id` BIGINT NOT NULL,
    `pitch_slot_id` BIGINT NOT NULL,
    `investor_id` BIGINT NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    FOREIGN KEY (`pitch_request_id`) REFERENCES `pitch_requests`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `pitch_booking_history` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `booking_id` BIGINT NOT NULL,
    `action` VARCHAR(50) NOT NULL,
    `old_slot_id` BIGINT NULL,
    `new_slot_id` BIGINT NULL,
    `created_at` DATETIME(6) NOT NULL,
    FOREIGN KEY (`booking_id`) REFERENCES `pitch_bookings`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `booking_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
