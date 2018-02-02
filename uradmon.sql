-- mysql -u root -p
-- create database uradmon ;
-- CREATE USER uradmon''@'localhost' identified by 'uradmon';
-- GRANT select, update, create, delete, insert ON uradmon.* to uradmon@localhost;
-- quit;
-- 
-- mysql -u root -p uradmon < uradmon.sql

CREATE TABLE `S129BG` (
`timestamp` int(11) NOT NULL,
`uuid` int(10)  DEFAULT NULL,
`utype` int(2) DEFAULT NULL,
`udetect`varchar (8) DEFAULT NULL,
`uvolt` int(4) DEFAULT NULL,
`ucpm` double  DEFAULT NULL,
`utemp` float (6.3) DEFAULT NULL,
`uhum` float (6.3) DEFAULT NULL,
`upres` int(8)  DEFAULT NULL,
`uvoc` int(8)  DEFAULT NULL,
`uc2o` int(8)  DEFAULT NULL,
`uch2o` float(6.3) DEFAULT NULL,
`upm25` int(6) DEFAULT NULL,
`uptime` int(16) DEFAULT NULL,
PRIMARY KEY (`timestamp`),
UNIQUE KEY `timestamp` (`timestamp`)
);
