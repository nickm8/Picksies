CREATE TABLE `list_movies` (
	`id` text PRIMARY KEY NOT NULL,
	`list_id` text NOT NULL,
	`movie_id` text NOT NULL,
	`watched` integer DEFAULT false,
	`added_at` text NOT NULL,
	`watched_at` text,
	`added_by_name` text,
	`created_at` integer NOT NULL,
	`updated_at` integer,
	FOREIGN KEY (`list_id`) REFERENCES `lists`(`id`) ON UPDATE no action ON DELETE cascade,
	FOREIGN KEY (`movie_id`) REFERENCES `movies`(`id`) ON UPDATE no action ON DELETE cascade
);
--> statement-breakpoint
CREATE TABLE `lists` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`description` text,
	`last_activity_at` text NOT NULL,
	`created_by_name` text,
	`created_at` integer NOT NULL,
	`updated_at` integer
);
--> statement-breakpoint
CREATE TABLE `movies` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`overview` text,
	`poster_path` text,
	`backdrop_path` text,
	`release_date` text,
	`vote_average` numeric,
	`runtime` integer,
	`external_movie_id` integer,
	`created_at` integer NOT NULL,
	`updated_at` integer
);
