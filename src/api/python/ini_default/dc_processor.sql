-- phpMyAdmin SQL Dump
-- version 3.4.11.1deb2+deb7u1
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Jan 20, 2015 at 04:59 AM
-- Server version: 5.5.40
-- PHP Version: 5.4.35-0+deb7u2

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `dc_processor`
--
CREATE DATABASE IF NOT EXISTS `dc_processor` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `dc_processor`;

-- --------------------------------------------------------

-- --------------------------------------------------------

--
-- Table structure for table `scraper_main`
--
DROP TABLE IF EXISTS `scraper_main`;
CREATE TABLE IF NOT EXISTS `scraper_main` (
  `Name` varchar(64) NOT NULL COMMENT 'Property''s name',
  `Hits` int(32) NOT NULL DEFAULT '0' COMMENT 'Count of hints by the article''s corpus',
  `Value` varchar(4096) NOT NULL COMMENT 'Property''s value',
  `User_Id` bigint(20) NOT NULL DEFAULT '0' COMMENT 'User Id',
  `CDate` datetime DEFAULT NULL COMMENT 'Creation date ',
  `UDate` datetime DEFAULT NULL COMMENT 'Modification date',
  KEY `Name` (`Name`),
  KEY `User_Id` (`User_Id`),
  KEY `Hits` (`Hits`),
  KEY `UDate` (`UDate`),
  KEY `CDate` (`CDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- Dumping data for table `scraper_main`
--

INSERT INTO `scraper_main` (`Name`, `Value`, `User_Id`, `CDate`, `UDate`) VALUES
('Scraper', '{"properties":{"algorithm":{"algorithm_name":"regular"},"modules":{"regular":["ScrapyExtractor","GooseExtractor","NewspaperExtractor","MLExtractor"],"concurrency":["NewspaperExtractor","ScrapyExtractor","GooseExtractor"],"training":["ScrapyExtractor","DiffBotExtractor"],"ML":["MLExtractor"],"SCRAPY":["ScrapyExtractor"],"GOOSE":["GooseExtractor"],"NEWSPAPER":["NewspaperExtractor"],"prediction":["MLExtractor"]}}}', 0, NULL, NULL),
('ScraperMultiItemsTask', '{"properties":{"algorithm":{"algorithm_name":"regular"},"modules":{"regular":["ScrapyExtractor","GooseExtractor","NewspaperExtractor","MLExtractor"],"concurrency":["NewspaperExtractor","ScrapyExtractor","GooseExtractor"],"training":["ScrapyExtractor","DiffBotExtractor"],"ML":["MLExtractor"],"SCRAPY":["ScrapyExtractor"],"GOOSE":["GooseExtractor"],"NEWSPAPER":["NewspaperExtractor"],"prediction":["MLExtractor"]}}}', 0, NULL, NULL),
('ScrapyExtractor', '{"properties":{"rank":1,"tags":{"content_encoded":{"rank":1},"pubdate":{"rank":1},"media":{"rank":1},"description":{"rank":1},"author":{"rank":1},"keywords":{"rank":1},"title":{"rank":1},"link":{"rank":1}},"template":"", "html5":1}}', 0, '2015-01-20 00:00:00', NULL),
('MLExtractor', '{"properties":{"rank":1,"tags":{"content_encoded":{"rank":1},"pubdate":{"rank":1},"media":{"rank":1},"description":{"rank":1},"author":{"rank":1},"keywords":{"rank":1},"title":{"rank":1},"link":{"rank":1}},"template":"", "html5":1}}', 0, NULL, NULL),
('NewspaperExtractor', '{"properties":{"rank":10,"tags":{"content_encoded":{"rank":1},"pubdate":{"rank":1},"media":{"rank":101},"description":{"rank":1},"author":{"rank":1},"keywords":{"rank":1},"title":{"rank":1},"link":{"rank":1}},"template":""}}', 0, NULL, NULL),
('GooseExtractor', '{"properties":{"rank":10,"tags":{"content_encoded":{"rank":1},"pubdate":{"rank":1},"media":{"rank":101},"description":{"rank":1},"author":{"rank":1},"keywords":{"rank":1},"title":{"rank":1},"link":{"rank":1}},"template":""}}', 0, NULL, NULL),
('BoilerpipeExtractor', '{"properties":{"rank":10,"tags":{"content_encoded":{"rank":1},"pubdate":{"rank":1},"media":{"rank":101},"description":{"rank":1},"author":{"rank":1},"keywords":{"rank":1},"title":{"rank":1},"link":{"rank":1}},"template":""}}', 0, NULL, NULL),
('AlchemyExtractor', '{"properties":{"rank":10,"tags":{"content_encoded":{"rank":1},"pubdate":{"rank":1},"media":{"rank":101},"description":{"rank":1},"author":{"rank":1},"keywords":{"rank":1},"title":{"rank":1},"link":{"rank":1}},"template":""}}', 0, NULL, NULL);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
