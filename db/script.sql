-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema certificacion
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `certificacion` ;

-- -----------------------------------------------------
-- Schema certificacion
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `certificacion` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `certificacion` ;

-- -----------------------------------------------------
-- Table `certificacion`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `certificacion`.`users` ;

CREATE TABLE IF NOT EXISTS `certificacion`.`users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `apellido` VARCHAR(100) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 10
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `certificacion`.`tutors`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `certificacion`.`tutors` ;

CREATE TABLE IF NOT EXISTS `certificacion`.`tutors` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `apellido` VARCHAR(100) NULL DEFAULT NULL,
  `email` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `certificacion`.`asesorias`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `certificacion`.`asesorias` ;

CREATE TABLE IF NOT EXISTS `certificacion`.`asesorias` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tema` VARCHAR(255) NOT NULL,
  `fecha` DATE NOT NULL,
  `duracion` INT NOT NULL,
  `notas` VARCHAR(50) NULL DEFAULT NULL,
  `usuario_id` INT NOT NULL,
  `tutor_id` INT NULL DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `usuario_id` (`usuario_id` ASC) VISIBLE,
  INDEX `tutor_id` (`tutor_id` ASC) VISIBLE,
  INDEX `idx_asesorias_fecha` (`fecha` ASC) VISIBLE,
  CONSTRAINT `asesorias_ibfk_1`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `certificacion`.`users` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `asesorias_ibfk_2`
    FOREIGN KEY (`tutor_id`)
    REFERENCES `certificacion`.`tutors` (`id`)
    ON DELETE SET NULL)
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
