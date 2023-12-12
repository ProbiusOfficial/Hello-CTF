#!/bin/bash

rm -f /docker-entrypoint.sh

mysqld_safe &

mysql_ready() {
	mysqladmin ping --socket=/run/mysqld/mysqld.sock --user=root --password=root > /dev/null 2>&1
}

while !(mysql_ready)
do
	echo "waiting for mysql ..."
	sleep 3
done

# Check the environment variables for the flag and assign to INSERT_FLAG
if [ "$DASFLAG" ]; then
    INSERT_FLAG="$DASFLAG"
elif [ "$FLAG" ]; then
    INSERT_FLAG="$FLAG"
elif [ "$GZCTF_FLAG" ]; then
    INSERT_FLAG="$GZCTF_FLAG"
else
    INSERT_FLAG="flag{TEST_Dynamic_FLAG}"
fi

echo "Run:insert into flag values('flag','$INSERT_FLAG');"

# 将FLAG写入文件 请根据需要修改
# echo $INSERT_FLAG | tee /home/$user/flag /flag

# 将FLAG写入数据库

if [[ -z $FLAG_COLUMN ]]; then
	FLAG_COLUMN="flag"
fi

if [[ -z $FLAG_TABLE ]]; then
	FLAG_TABLE="flag"
fi

mysql -u root -p123456 -e "
USE ctf;
create table $FLAG_TABLE (id varchar(300),data varchar(300));
insert into $FLAG_TABLE values('$FLAG_COLUMN','$INSERT_FLAG');
"

php-fpm & nginx &

echo "Running..."

tail -F /var/log/nginx/access.log /var/log/nginx/error.log