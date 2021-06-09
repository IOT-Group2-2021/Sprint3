-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Mar 14, 2021 at 06:21 PM
-- Server version: 8.0.21
-- PHP Version: 7.4.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `iot-group2`
--
CREATE DATABASE IF NOT EXISTS `iot-group2` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `iot-group2`;

-- --------------------------------------------------------

--
-- Table structure for table `Payloads`
--

CREATE TABLE `Payloads` (
  `payloadID` int NOT NULL,
  `appID` varchar(30) NOT NULL,
  `deviceID` varchar(30) NOT NULL,
  `hardwareSerial` varchar(30) NOT NULL,
  `port` int NOT NULL,
  `datetime` datetime NOT NULL,
  `payloadContent` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Payloads`
--
ALTER TABLE `Payloads`
  ADD PRIMARY KEY (`payloadID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Payloads`
--
ALTER TABLE `Payloads`
  MODIFY `payloadID` int NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
