sudo su
su oracle
pkill -u oracle

/oracle/fmw12.2.1/product/Oracle_Home/oracle_common/bin/rcu -silent -dropRepository -databaseType ORACLE -connectString tds99np.cqtdwxgp6ypj.ap-southeast-2.rds.amazonaws.com:1521:tds99np -dbUser something_like_user -dbRole Normal -schemaPrefix wls12c2  -component ODI  -component IAU -component IAU_APPEND -component IAU_VIEWER -component OPSS -component STB -f < /oracle/fmw12.2.1/installer/odi_rcu_paramfile.txt

rm -rf /oracle/fmw12.2.1/config

