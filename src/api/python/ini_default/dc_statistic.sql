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
CREATE DATABASE IF NOT EXISTS `dc_statistic` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_statistic`;

-- --------------------------------------------------------

--
-- Table structure for table `process_statistic`
--

DROP TABLE IF EXISTS `process_statistic`;
CREATE TABLE IF NOT EXISTS `process_statistic` (
  `Site_Id` varchar(32) DEFAULT '0',
  `URLMD5` varchar(32) NOT NULL DEFAULT '',
  `Extractor` varchar(128) NOT NULL DEFAULT '',
  `WordsCount` int(10) unsigned NOT NULL DEFAULT '0',
  `UnicWordsCount` int(10) unsigned NOT NULL DEFAULT '0',
  `GoodWordsCount` int(10) unsigned NOT NULL DEFAULT '0',
  KEY `Site_Id` (`Site_Id`),
  KEY `URLMD5` (`URLMD5`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
