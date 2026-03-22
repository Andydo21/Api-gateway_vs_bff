CREATE DATABASE IF NOT EXISTS matchmaking_db;
USE matchmaking_db;

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
