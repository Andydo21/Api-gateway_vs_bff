-- DDL Script for Microservices Project (MySQL Version)
-- Generated based on Django Models

CREATE DATABASE IF NOT EXISTS microservices;
USE microservices;

-- ================================================
-- 👤 USER SERVICE
-- ================================================

CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `password` VARCHAR(128) NOT NULL,
    `last_login` DATETIME(6) NULL,
    `is_superuser` BOOLEAN NOT NULL DEFAULT 0,
    `username` VARCHAR(150) NOT NULL UNIQUE,
    `first_name` VARCHAR(150) NOT NULL,
    `last_name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(254) NOT NULL,
    `is_staff` BOOLEAN NOT NULL DEFAULT 0,
    `is_active` BOOLEAN NOT NULL DEFAULT 1,
    `date_joined` DATETIME(6) NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `role` VARCHAR(20) NOT NULL DEFAULT 'user',
    `banned` BOOLEAN NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `user_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 🚀 STARTUP SERVICE
-- ================================================

CREATE TABLE IF NOT EXISTS `startup_categories` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `startups` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NULL,
    `company_name` VARCHAR(255) NULL,
    `description` TEXT NULL,
    `industry` VARCHAR(100) NULL,
    `website` VARCHAR(255) NULL,
    `category_id` BIGINT NULL,
    `image_url` VARCHAR(200) NOT NULL,
    `featured` BOOLEAN NOT NULL DEFAULT 0,
    `status` VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL,
    FOREIGN KEY (`category_id`) REFERENCES `startup_categories`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `investors` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL UNIQUE,
    `company_name` VARCHAR(255) NOT NULL,
    `bio` TEXT NOT NULL,
    `interests` VARCHAR(255) NULL,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `reviews` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `startup_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL,
    `username` VARCHAR(255) NOT NULL DEFAULT 'Khách hàng',
    `rating` INT NOT NULL,
    `comment` TEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    FOREIGN KEY (`startup_id`) REFERENCES `startups`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `startup_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 📅 SCHEDULING SERVICE
-- ================================================

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
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 📝 BOOKING SERVICE
-- ================================================

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


-- ================================================
-- 💳 FUNDING SERVICE
-- ================================================

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
    `processed_at?` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 💬 FEEDBACK SERVICE
-- ================================================

CREATE TABLE IF NOT EXISTS `feedbacks` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `booking_id` BIGINT NOT NULL,
    `investor_id` BIGINT NOT NULL,
    `rating` INT NOT NULL DEFAULT 5,
    `comment` TEXT NOT NULL,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `investment_interests` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `booking_id` BIGINT NOT NULL,
    `investor_id` BIGINT NOT NULL,
    `status` VARCHAR(20) NOT NULL,
    `note` TEXT NULL,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `feedback_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload?` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 📦 RESOURCE SERVICE
-- ================================================

CREATE TABLE IF NOT EXISTS `event_resources` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `startup_id` BIGINT NOT NULL UNIQUE,
    `startup_name` VARCHAR(255) NOT NULL,
    `available_quantity` INT NOT NULL DEFAULT 0,
    `reserved_quantity` INT NOT NULL DEFAULT 0,
    `reorder_level` INT NOT NULL DEFAULT 10,
    `last_restocked` DATETIME(6) NULL,
    `created_at` DATETIME(6) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL
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


-- ================================================
-- 🔍 MATCHMAKING SERVICE
-- ================================================

CREATE TABLE IF NOT EXISTS `user_interactions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `startup_id` BIGINT NOT NULL,
    `interaction_type` VARCHAR(20) NOT NULL,
    `weight` DOUBLE NOT NULL DEFAULT 1.0,
    `metadata` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    INDEX (`user_id`, `startup_id`),
    INDEX (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `startup_similarities` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `startup_id` BIGINT NOT NULL,
    `similar_startup_id` BIGINT NOT NULL,
    `similarity_score` DOUBLE NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    UNIQUE KEY (`startup_id`, `similar_startup_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `matchmaking_outbox_events` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `event_type` VARCHAR(100) NOT NULL,
    `payload` JSON NOT NULL,
    `created_at` DATETIME(6) NOT NULL,
    `processed` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 🤝 MEETING SERVICE
-- ================================================

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
    `processed?` BOOLEAN NOT NULL DEFAULT 0,
    `processed_at?` DATETIME(6) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ================================================
-- 🔔 NOTIFICATION SERVICE
-- ================================================

CREATE TABLE IF NOT EXISTS `notifications` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT NOT NULL,
    `message` TEXT NOT NULL,
    `notification_type` VARCHAR(20) NOT NULL DEFAULT 'info',
    `is_read` BOOLEAN NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
