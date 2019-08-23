#wls parameters
domain_application_home = '{{ applications_home }}/{{ domain_name }}'
domain_configuration_home = '{{ domains_home }}/{{ domain_name }}'
domain_name = '{{ domain_name }}'
java_home = '{{ jdk_folder }}'
middleware_home = '{{ middleware_home }}'
#node_manager_home = '{{ nodemanager_home }}'  
weblogic_home = '{{ weblogic_home }}'

#database
db_server_name = '{{ dbserver_name }}'
db_server_port = '{{ dbserver_port }}'
db_service = '{{ dbserver_service }}'
db_url = 'jdbc:oracle:thin:@//' + db_server_name + ':' + db_server_port + '/' + db_service;
db_user = '{{ repository_prefix }}_STB'   
db_password = '{{ datasource_password }}'
db_driver = 'oracle.jdbc.OracleDriver'
data_source_user_prefix= '{{ repository_prefix }}'
data_source_test='SQL SELECT 1 FROM DUAL';
supervisor_user = '{{ supervisor_user }}'
supervisor_password = '{{ supervisor_password }}'
nm_name = '{{ node_manager_name }}'
nm_port = '{{ node_manager_listen_port }}'

#admin server
host_name = '{{ server_hostname }}'
admin_user = '{{ weblogic_admin }}'
admin_password = '{{ weblogic_admin_pass }}'
admin_port = '{{ admin_server_port }}'

#cluster and managed server
server_hostname               = '{{ server_hostname }}'
server_port                   = int('{{ managed_server_port }}')
managed_server_name_base      = '{{ managed_server_name }}'
number_of_ms                  = int('{{ managed_server_count }}')
cluster_name                  = '{{ cluster_name }}'
cluster_type                  = '{{ cluster_type }}'
production_mode_enabled       = '{{ prod_mode_enabled }}'

selectTemplate('Basic WebLogic Server Domain')
loadTemplates()
setOption('DomainName', domain_name);
setOption('OverwriteDomain', 'true');
setOption('JavaHome', java_home);
setOption('ServerStartMode', 'prod');
# not applicable for 12.2.1
#setOption('NodeManagerType', 'CustomLocationNodeManager');
#setOption('NodeManagerHome', node_manager_home);
cd('/Security/base_domain/User/{{ weblogic_admin }}');
cmo.setName('{{ weblogic_admin }}');
cmo.setUserPassword('{{ weblogic_admin_pass }}');
cd('/');

print "SAVE DOMAIN";
writeDomain(domain_configuration_home);
closeTemplate();

print 'READ DOMAIN';
readDomain(domain_configuration_home);

print 'ADD TEMPLATES';
selectTemplate('Oracle Enterprise Manager Plugin for ODI')
selectTemplate('Oracle Data Integrator - Agent')
selectTemplate('Oracle Data Integrator - Console')
selectTemplate('Oracle Data Integrator - JRF Async Web Services')
loadTemplates()
# not needed em template will add them
#addTemplate(jrf_template);
#addTemplate(coherence_template);
setOption('AppDir', domain_application_home);


print('CREATE DATA SOURCE')
jdbcsystemresources = cmo.getJDBCSystemResources();
for jdbcsystemresource in jdbcsystemresources:
    cd ('/JDBCSystemResource/' + jdbcsystemresource.getName() + '/JdbcResource/' + jdbcsystemresource.getName() + '/JDBCConnectionPoolParams/NO_NAME_0');
    cmo.setInitialCapacity(1);
    cmo.setMaxCapacity(15);
    cmo.setMinCapacity(1);
    cmo.setStatementCacheSize(0);
    cmo.setTestConnectionsOnReserve(java.lang.Boolean('false'));
    cmo.setTestTableName(data_source_test);
    cmo.setConnectionCreationRetryFrequencySeconds(30);
    cd ('/JDBCSystemResource/' + jdbcsystemresource.getName() + '/JdbcResource/' + jdbcsystemresource.getName() + '/JDBCDriverParams/NO_NAME_0');
    cmo.setUrl(db_url);
    cmo.setPasswordEncrypted('{{ datasource_password }}');
   
    cd ('/JDBCSystemResource/' + jdbcsystemresource.getName() + '/JdbcResource/' + jdbcsystemresource.getName() + '/JDBCDriverParams/NO_NAME_0/Properties/NO_NAME_0/Property/user');
    cmo.setValue(cmo.getValue().replace('DEV',data_source_user_prefix));
    cd('/');


cd("/SecurityConfiguration/" + domain_name);
cmo.setNodeManagerUsername('{{ nodemanager_username }}');
cmo.setNodeManagerPasswordEncrypted('{{ nodemanager_password }}');

print('Create node manager.')
cd('/')
machine = create(nm_name, 'UnixMachine')
cd('Machines/' + nm_name)
create(nm_name, 'NodeManager')
cd('NodeManager/' + nm_name)
set('ListenAddress', host_name)
set('ListenPort', int(nm_port))

#print('Create machine - {{ server_hostname }} ')
#cd('/')
#machine = create('{{ server_hostname }}', 'UnixMachine')
##cd('/Machines/' + '{{ server_hostname }}' + '/NodeManager/' + '{{ server_hostname }}')
#cd('/Machines/' + '{{ server_hostname }}')
#set('ListenAddress', '{{ node_manager_listen_address }}')


print('{{ admin_server_name }} settings.')
cd('/Server/' + '{{ admin_server_name }}');
create('{{ admin_server_name }}','SSL');
cd('SSL/' + '{{ admin_server_name }}');
cmo.setHostnameVerificationIgnored(true);
cmo.setHostnameVerifier(None);
cmo.setTwoWaySSLEnabled(false);
cmo.setClientCertificateEnforced(false);

cd('/SecurityConfiguration/'+ domain_name +'/Realms/myrealm');
cd('AuthenticationProviders/DefaultAuthenticator');
set('ControlFlag', 'SUFFICIENT');
cd('../../');

print('Create supervisor credential.')
cd("/SecurityConfiguration/" + domain_name);
cmo.setUseKSSForDemo(false)
cd('/Credential/TargetStore/oracle.odi.credmap/TargetKey/SUPERVISOR')
create('c','Credential')
cd('Credential')
cmo.setUsername(supervisor_user)
cmo.setPassword(supervisor_password)

#getDatabaseDefaults()

# Create a cluster
# ================
cd('/')
cl=create(cluster_name, 'Cluster')

if cluster_type == "CONFIGURED":

  # Create managed servers
  for index in range(0, number_of_ms):
    cd('/')
    msIndex = index+1

    cd('/')
    name = '%s%s' % (managed_server_name_base, msIndex)

    create(name, 'Server')
    cd('/Servers/%s/' % name )
    print('managed server name is %s' % name);
    set('ListenAddress', server_hostname)
    set('ListenPort', server_port)
    set('NumOfRetriesBeforeMSIMode', 0)
    set('RetryIntervalBeforeMSIMode', 1)
    set('Cluster', cluster_name)
    set('Machine', '{{ node_manager_name }}')
    

  applyJRF(target=cluster_name , domainDir='{{ domain_home }}');

else:
  print('Configuring Dynamic Cluster %s' % cluster_name)

  templateName = cluster_name + "-template"
  print('Creating Server Template: %s' % templateName)
  st1=create(templateName, 'ServerTemplate')
  print('Done creating Server Template: %s' % templateName)
  cd('/ServerTemplates/%s' % templateName)
  cmo.setListenAddress(server_hostname)
  cmo.setListenPort(server_port)
  cmo.setCluster(cl)
  #cmo.setMachine(getMBean('/Machines/' + '{{ server_hostname }}'))

  cd('/Clusters/%s' % cluster_name)
  create(cluster_name, 'DynamicServers')
  cd('DynamicServers/%s' % cluster_name)
  set('ServerTemplate', st1)
  set('ServerNamePrefix', managed_server_name_base)
  set('DynamicClusterSize', number_of_ms)
  set('MaxDynamicClusterSize', number_of_ms)
  set('CalculatedListenPorts', false)
  set('CalculatedMachineNames', true)
  set('MachineNameMatchExpression', '{{ node_manager_name }}*' )
  applyJRF(target=cluster_name , domainDir='{{ domain_home }}');
  print('Done setting attributes for Dynamic Cluster: %s' % cluster_name);
  
  cd('/')
if production_mode_enabled == "true":
  cmo.setProductionModeEnabled(true)
else:
  cmo.setProductionModeEnabled(false)


print('Write the domain and close the template.')


updateDomain();
closeDomain();
