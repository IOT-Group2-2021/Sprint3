-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: db
-- Generation Time: May 04, 2021 at 10:37 AM
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
-- Table structure for table `heatsensor`
--

CREATE TABLE `heatsensor` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `temperature` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `noisesensor`
--

CREATE TABLE `noisesensor` (
  `IDpayload` int NOT NULL,
  `datetime` datetime NOT NULL,
  `noise` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `heatsensor`
--
ALTER TABLE `heatsensor`
  ADD PRIMARY KEY (`IDpayload`);

--
-- Indexes for table `noisesensor`
--
ALTER TABLE `noisesensor`
  ADD PRIMARY KEY (`IDpayload`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `heatsensor`
--
ALTER TABLE `heatsensor`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `noisesensor`
--
ALTER TABLE `noisesensor`
  MODIFY `IDpayload` int NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
