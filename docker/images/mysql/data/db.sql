-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: Jun 15, 2021 at 11:43 AM
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
-- Table structure for table `concentration`
--

CREATE TABLE `concentration` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `data (ppm)` int UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `loudness`
--

CREATE TABLE `loudness` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `data (mV)` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `presence`
--

CREATE TABLE `presence` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `data (boolean)` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `pressure`
--

CREATE TABLE `pressure` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `data (hPa)` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `rh`
--

CREATE TABLE `rh` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `data (%)` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `temperature`
--

CREATE TABLE `temperature` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `data (°C)` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `concentration`
--
ALTER TABLE `concentration`
  ADD PRIMARY KEY (`IDpayload`);

--
-- Indexes for table `loudness`
--
ALTER TABLE `loudness`
  ADD PRIMARY KEY (`IDpayload`);

--
-- Indexes for table `presence`
--
ALTER TABLE `presence`
  ADD PRIMARY KEY (`IDpayload`);

--
-- Indexes for table `pressure`
--
ALTER TABLE `pressure`
  ADD PRIMARY KEY (`IDpayload`);

--
-- Indexes for table `rh`
--
ALTER TABLE `rh`
  ADD PRIMARY KEY (`IDpayload`);

--
-- Indexes for table `temperature`
--
ALTER TABLE `temperature`
  ADD PRIMARY KEY (`IDpayload`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `concentration`
--
ALTER TABLE `concentration`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `loudness`
--
ALTER TABLE `loudness`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `presence`
--
ALTER TABLE `presence`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `pressure`
--
ALTER TABLE `pressure`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `rh`
--
ALTER TABLE `rh`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `temperature`
--
ALTER TABLE `temperature`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
