#!/usr/bin/python

print('Set variables.')
host_name = '{{ server_hostname }}'
admin_user = '{{ weblogic_admin }}'
admin_password = '{{ weblogic_admin_pass }}'
admin_port = '{{ admin_server_port }}'
mw_home = '{{ middleware_home }}'
domain_name = '{{ domain_name }}'
domain_home = '{{ domains_home }}/{{ domain_name }}'   # Check path is correct.
wl_home = '{{ weblogic_home }}'


#database
db_server_name = '{{ dbserver_name }}'
db_server_port = '{{ dbserver_port }}'
db_service = '{{ dbserver_service }}'
db_url = 'jdbc:oracle:thin:@//' + db_server_name + ':' + db_server_port + '/' + db_service;
db_user = '{{ repository_prefix }}_STB'   
db_password = '{{ datasource_password }}'
db_driver = 'oracle.jdbc.OracleDriver'
odi_port = '{{ odi_server_port }}'
supervisor_user = '{{ supervisor_user }}'
supervisor_password = '{{ supervisor_password }}'
nm_name = '{{ node_manager_listen_address }}'
nm_port = '{{ node_manager_listen_port }}'

print('Create domain (' + domain_name + ').')
print('Load templates.')
selectTemplate('Basic WebLogic Server Domain')
selectTemplate('Oracle Enterprise Manager Plugin for ODI')
selectTemplate('Oracle Data Integrator - Agent')
selectTemplate('Oracle Data Integrator - Console')
selectTemplate('Oracle Data Integrator - JRF Async Web Services')
loadTemplates()

print('AdminServer settings.') #todo : must come from inventory
cd('/Security/base_domain/User/' + admin_user)
cmo.setPassword(admin_password)
cd('/Server/AdminServer')
cmo.setName('AdminServer')
cmo.setListenPort(int(admin_port))
cmo.setListenAddress(host_name)

print('Create supervisor credential.')
cd('/SecurityConfiguration/base_domain')
cmo.setUseKSSForDemo(false)
cd('/Credential/TargetStore/oracle.odi.credmap/TargetKey/SUPERVISOR')
create('c','Credential')
cd('Credential')
cmo.setUsername(supervisor_user)
cmo.setPassword(supervisor_password)

print('Create data source.')
cd('/JDBCSystemResource/LocalSvcTblDataSource/JdbcResource/LocalSvcTblDataSource/JDBCDriverParams/NO_NAME_0')
cmo.setPasswordEncrypted(db_password)
cmo.setUrl(db_url)
cmo.setDriverName(db_driver)
cd('Properties/NO_NAME_0/Property/user')
cmo.setValue(db_user)

#cd('/');

#cd("/SecurityConfiguration/" + domain_name);
#cmo.setNodeManagerUsername('{{ nodemanager_username }}');
#cmo.setNodeManagerPasswordEncrypted('{{ nodemanager_password }}');

#cd('/Server/' + '{{ admin_server_name }}');
#create('{{ admin_server_name }}','SSL');
#cd('SSL/' + '{{ admin_server_name }}');
#cmo.setHostnameVerificationIgnored(true);
#cmo.setHostnameVerifier(None);
#cmo.setTwoWaySSLEnabled(false);
#cmo.setClientCertificateEnforced(false);
#
#cd('/SecurityConfiguration/'+ domain_name +'/Realms/myrealm');
#cd('AuthenticationProviders/DefaultAuthenticator');
#set('ControlFlag', 'SUFFICIENT');
#cd('../../');
#
#updateDomain();
#closeDomain();

print('Create node manager.')
cd('/')
machine = create(nm_name, 'UnixMachine')
cd('Machines/' + nm_name)
create(nm_name, 'NodeManager')
cd('NodeManager/' + nm_name)
set('ListenAddress', host_name)
set('ListenPort', int(nm_port))

print('Associate Node Nanager with servers.')
cd('/Servers/AdminServer')
cmo.setMachine(machine)
cd('/Servers/ODI_server1')
cmo.setMachine(machine)

print('ODI_server1 settings')
cd('/Servers/ODI_server1')
cmo.setListenAddress(host_name)
cmo.setListenPort(int(odi_port))

getDatabaseDefaults()

print('Run in production mode.')
setOption('ServerStartMode','prod')

print('Write the domain and close the template.')
setOption('OverwriteDomain', 'true')
writeDomain(domain_home)
closeTemplate()

exit()

