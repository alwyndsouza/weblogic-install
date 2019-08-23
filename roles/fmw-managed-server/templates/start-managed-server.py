managed_server_name_base      = '{{ managed_server_name }}'
number_of_ms                  = int('{{ managed_server_count }}')

connect('{{ weblogic_admin }}', '{{ weblogic_admin_pass }}')
start('{{ cluster_name }}','Cluster')

#for index in range(0, number_of_ms):
#  msIndex = index+1
#  name = '%s%s' % (managed_server_name_base, msIndex)
#  start(name)
#  print('Started managed server name is %s' % name);

#nmConnect('{{ nodemanager_username }}', '{{ nodemanager_password }}', '{{ node_manager_listen_address }}', '{{ node_manager_listen_port }}', '{{ domain_name }}');
#nmStart('{{ managed_server_name }}');
#nmDisconnect();
