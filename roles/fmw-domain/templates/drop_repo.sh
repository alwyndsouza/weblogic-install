#!/bin/bash

SCRIPT=$(readlink -f $0)
SCRIPT_PATH=$(dirname $SCRIPT)

JAVA_HOME={{ jdk_folder }}
export JAVA_HOME

{{ middleware_home }}/oracle_common/bin/rcu -silent -dropRepository -databaseType ORACLE -connectString {{ dbserver_name }}:{{ dbserver_port }}:{{ dbserver_service }} -dbUser {{ master_user }} -dbRole Normal  -schemaPrefix {{ repository_prefix }} true -component ODI  -component IAU -component IAU_APPEND -component IAU_VIEWER -component OPSS -component STB -f < {{ mw_installer_folder }}/odi_rcu_paramfile.txt
