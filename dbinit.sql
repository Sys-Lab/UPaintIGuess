drop database if exists guesswhat;

create database guesswhat;

use guesswhat;

create table a_usrs (
    `t_uid` INT(10) NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `t_username` varchar(32) not null,
    `t_password` varchar(32) not null,
    `t_emailaddr` varchar(128) not null,
    `t_gender` tinyint(2) not null,
    `t_privilege` tinyint(1),
    `t_credits` int(10),
    `t_created_at` real
) engine=innodb default charset=utf8;

create table a_usrext (
    `t_uid` int(10) not null primary key,
    `t_qqid` varchar(12),
    `t_cellphone` varchar(11),
    `t_zipcode` varchar(6),
    `t_rank` tinyint(2),
    `t_avatar` text,
    `t_motto` varchar(200),
    `t_website` varchar(72),
    `t_birthday` real
) engine=innodb default charset=utf8;

create table a_words (
    `t_id` int(9) not null primary key auto_increment,
    `t_word` varchar(16),
    `t_desc` varchar(24)
) engine=innodb default charset=utf8;