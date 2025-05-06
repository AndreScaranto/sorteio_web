-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema sorteio_web
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema sorteio_web
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `sorteio_web` DEFAULT CHARACTER SET utf8 ;
USE `sorteio_web` ;

-- -----------------------------------------------------
-- Table `sorteio_web`.`sorteio`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sorteio_web`.`sorteio` ;

CREATE TABLE IF NOT EXISTS `sorteio_web`.`sorteio` (
  `id_sorteio` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(45) NOT NULL,
  `data_limite` TIMESTAMP NOT NULL,
  `realizado` TINYINT NULL DEFAULT 0,
  `id_bilhete_sorteado` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id_sorteio`),
  UNIQUE INDEX `nome_UNIQUE` (`nome` ASC) VISIBLE,
  INDEX `fk_sorteio_bilhete1_idx` (`id_bilhete_sorteado` ASC) VISIBLE,
  CONSTRAINT `fk_sorteio_bilhete1`
    FOREIGN KEY (`id_bilhete_sorteado`)
    REFERENCES `sorteio_web`.`bilhete` (`id_bilhete`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `sorteio_web`.`bilhete`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sorteio_web`.`bilhete` ;

CREATE TABLE IF NOT EXISTS `sorteio_web`.`bilhete` (
  `id_bilhete` INT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(45) NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `sobrenome` VARCHAR(45) NOT NULL,
  `celular` VARCHAR(45) NOT NULL,
  `id_sorteio` INT NOT NULL,
  PRIMARY KEY (`id_bilhete`),
  UNIQUE INDEX `id_UNIQUE` (`id_bilhete` ASC) VISIBLE,
  UNIQUE INDEX `codigo_UNIQUE` (`codigo` ASC) VISIBLE,
  INDEX `fk_bilhete_sorteio_idx` (`id_sorteio` ASC) VISIBLE,
  CONSTRAINT `fk_bilhete_sorteio`
    FOREIGN KEY (`id_sorteio`)
    REFERENCES `sorteio_web`.`sorteio` (`id_sorteio`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `sorteio_web`.`administrador`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sorteio_web`.`administrador` ;

CREATE TABLE IF NOT EXISTS `sorteio_web`.`administrador` (
  `id_admin` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`id_admin`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `sorteio_web`.`codigo`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `sorteio_web`.`codigo` ;

CREATE TABLE IF NOT EXISTS `sorteio_web`.`codigo` (
  `id_codigo` INT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(45) NOT NULL,
  `id_sorteio` INT NOT NULL,
  PRIMARY KEY (`id_codigo`),
  UNIQUE INDEX `codigo_UNIQUE` (`codigo` ASC) VISIBLE,
  INDEX `fk_codigo_sorteio1_idx` (`id_sorteio` ASC) VISIBLE,
  CONSTRAINT `fk_codigo_sorteio1`
    FOREIGN KEY (`id_sorteio`)
    REFERENCES `sorteio_web`.`sorteio` (`id_sorteio`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
