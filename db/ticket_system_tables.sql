-- Create Tickets table
CREATE TABLE IF NOT EXISTS `Tickets` (
    `TicketId` INT AUTO_INCREMENT PRIMARY KEY,
    `TicketType` VARCHAR(255) NOT NULL,
    `CreatorUserId` BIGINT UNSIGNED NOT NULL,
    `CreatorUsername` VARCHAR(255) NOT NULL,
    `ServerId` BIGINT UNSIGNED NOT NULL,
    `ThreadId` BIGINT UNSIGNED NULL,
    `AssignedStaffUserId` BIGINT UNSIGNED NULL,
    `Status` VARCHAR(50) NOT NULL DEFAULT 'open',
    `CreatedAt` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `ClosedAt` DATETIME NULL,
    `ClosureReason` TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create TicketMessages table
CREATE TABLE IF NOT EXISTS `TicketMessages` (
    `MessageId` INT AUTO_INCREMENT PRIMARY KEY,
    `TicketId` INT NOT NULL,
    `SenderUserId` BIGINT UNSIGNED NOT NULL,
    `SenderUsername` VARCHAR(255) NOT NULL,
    `MessageContent` TEXT NOT NULL,
    `Timestamp` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`TicketId`) REFERENCES `Tickets`(`TicketId`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS `IX_Tickets_Status` ON `Tickets`(`Status`);
CREATE INDEX IF NOT EXISTS `IX_Tickets_CreatedAt` ON `Tickets`(`CreatedAt`);
CREATE INDEX IF NOT EXISTS `IX_Tickets_ServerId` ON `Tickets`(`ServerId`);
CREATE INDEX IF NOT EXISTS `IX_TicketMessages_TicketId` ON `TicketMessages`(`TicketId`); 