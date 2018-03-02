-- phpMyAdmin SQL  Dump
-- version 4.1.12
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 15, 2014 at 10:35 AM
-- Server version: 5.5.35-0+wheezy1
-- PHP Version: 5.4.4-14+deb7u8

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `dc_sites`
--
CREATE DATABASE IF NOT EXISTS `dc_contents` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_contents`;

-- --------------------------------------------------------


CREATE TABLE IF NOT EXISTS `contents_0` (
  `id` varchar(32) NOT NULL DEFAULT '0',
  `data` longblob NOT NULL,
  `CDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY `id` (`id`),
  KEY `CDate` (`CDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
