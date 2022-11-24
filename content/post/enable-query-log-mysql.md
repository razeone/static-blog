---
title: "Enable Query Log Mysql"
date: 2022-11-23T20:15:54-06:00
thumbnail: "images/mysql.jpg"
Description: "How to enable query log in mysql"
Tags: ["mysql", "query log"]
Categories: ["mysql"]
---


Hello people, this time I'll use this blog post a a placeholder for a snippet that is useful when working with My
SQL and specially if you're having trouble understanding behaviours on your database.

# Enable Query Log Mysql

There are a couple of options when you want to enable query log on your database, the first one is to use the following configuration:

For MySQL 5.1.28 and older, edit the `/etc/my.cnf` file and in the `[mysqld]` section add the following line:

```bash
log_output = /path/to/file.log
```

[Source](http://dev.mysql.com/doc/refman/5.1/en/query-log.html)


For mysql 5.1.29 and newer, edit the `/etc/my.cnf` file and in the `[mysqld]` section add the following line:

```bash
general_log = 1
general_log_file = /path/to/file.log
```

And finally, restart the MySQL server:

```bash
sudo service mysql restart
```

Alternatively if you cannot restart the server, you can use the following commands:

```bash
SET GLOBAL general_log = 1;
SET global log_output = 'table';
```

Then to see the log, you can use the following command:

```bash
SELECT * FROM mysql.general_log;
```

After your debugging has finished, you can turn off the query log by using the following command:

```bash
SET GLOBAL general_log = 0;
```

And truncate the table by using the following command:

```bash
TRUNCATE TABLE mysql.general_log;
```

I hope this helps you to debug your database.

Cheers!