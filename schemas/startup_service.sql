CREATE DATABASE IF NOT EXISTS startup_db;
USE startup_db;

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
