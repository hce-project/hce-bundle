-- Create table `titles_cache` for `news_hub` database
-- --------------------------------------------------------
--
-- Table structure for table `titles_cache`
--
USE `news_hub`;

CREATE TABLE IF NOT EXISTS `titles_cache` (
  `Id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,  
  `URLMd5` varchar(32) NOT NULL DEFAULT '',
  `URL` varchar(4096) NOT NULL DEFAULT '',
  `Title` varchar(1000) NOT NULL DEFAULT '',
  `CDate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `URLMd5` (`URLMd5`),
  KEY `CDate` (`CDate`)    
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


INSERT INTO `titles_cache` (`URLMd5`, `URL`, `Title`) VALUES 
(MD5('http://www.pcadvisor.co.uk/buying-advice/google-android/best-android-vr-apps-games-top-virtual-reality-apps-for-android-3654381/'), 'http://www.pcadvisor.co.uk/buying-advice/google-android/best-android-vr-apps-games-top-virtual-reality-apps-for-android-3654381/', 'Best Android VR apps and games: The top virtual reality apps for Android'),
(MD5('http://feedproxy.google.com/~r/techradar/allnews/~3/7EZwKJ6AnCE/youtube-now-has-an-offline-viewing-app-for-android'), 'http://feedproxy.google.com/~r/techradar/allnews/~3/7EZwKJ6AnCE/youtube-now-has-an-offline-viewing-app-for-android', 'YouTube now has an offline viewing app for Android'),
(MD5('http://www.computerworld.com/article/3164539/android/balancing-security-and-convenience-on-your-android-phone.html'), 'http://www.computerworld.com/article/3164539/android/balancing-security-and-convenience-on-your-android-phone.html', 'Balancing security and convenience on your Android phone'),
(MD5('http://www.infoworld.com/article/3167547/android/the-android-wear-20-terror-and-other-fake-news.html'), 'http://www.infoworld.com/article/3167547/android/the-android-wear-20-terror-and-other-fake-news.html', 'The Android Wear 2.0 terror and other fake news'),
(MD5('http://www.pcworld.com/article/3167684/android/the-six-android-wear-20-changes-you-should-check-out-first.html'), 'http://www.pcworld.com/article/3167684/android/the-six-android-wear-20-changes-you-should-check-out-first.html', 'The six Android Wear 2.0 changes you should check out first'),
(MD5('http://www.theinquirer.net/inquirer/news/3004281/android-wear-20-debuts-on-the-lg-watch-sport-and-watch-style'), 'http://www.theinquirer.net/inquirer/news/3004281/android-wear-20-debuts-on-the-lg-watch-sport-and-watch-style', 'Android Wear 2.0 debuts on the LG Watch Sport and Watch Style'),
(MD5('https://www.cnet.com/news/strava-runkeeper-android-wear-2-update/'), 'https://www.cnet.com/news/strava-runkeeper-android-wear-2-update/', 'Strava and Runkeeper bring GPS tracking to Android Wear 2.0'),
(MD5('http://hothardware.com/news/google-debuts-android-wear-20-with-the-lg-watch-sport-and-watch-style/'), 'http://hothardware.com/news/google-debuts-android-wear-20-with-the-lg-watch-sport-and-watch-style/', 'Google Debuts Android Wear 2.0 With the LG Watch Sport And Watch Style')
