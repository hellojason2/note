CREATE TABLE `notes` (
	`id` varchar(64) NOT NULL,
	`slug` varchar(255) NOT NULL,
	`title` text NOT NULL,
	`content` text NOT NULL,
	`password` varchar(255),
	`userId` varchar(64) NOT NULL,
	`createdAt` timestamp DEFAULT (now()),
	`updatedAt` timestamp DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `notes_id` PRIMARY KEY(`id`),
	CONSTRAINT `notes_slug_unique` UNIQUE(`slug`)
);
