#!/usr/bin/python

# Copyright (c) 2011, 2014, Oracle and/or its affiliates. All rights reserved.
#
# This script creates domain, extends domain with all ODI templates 
# and finally configures master and work datasources on managed server

import os, sys

###############################################################################
# Set approriate values for following variable as per your environment
###############################################################################

# gets hostname from the OS
host_name = os.getenv('HOSTNAME');

# Middleware Home of your environment
mw_home='{{ middleware_home }}';

# odi folder location under middleware home
odi_oracle_home= mw_home + "/odi";

# WLS domain directory. Update as appropriate
wls_domain_dir='{{ domain_home }}';

# Domain name for the Odi Jee Agent
wls_domain_name='{{ domain_home }}';

# Weblogic admin user name
wls_user='{{ weblogic_admin }}'

# Weblogic admin user's password
wls_pass='{{ weblogic_admin_pass }}';

# The STB schema username created through RCU. Ends with _STB
# ODI Master and Work repository and Opss database connections are fetched from
# this schema
service_db_user= '{{ repository_prefix }}_STB';   

# STB users password
service_db_pass='{{ datasource_password }}';

# JDBC URL to the STB database
# Make sure to use the right URL format
db_server_name = '{{ dbserver_name }}'
db_server_port = '{{ dbserver_port }}'
db_service = '{{ dbserver_service }}'
service_db_url='jdbc:oracle:thin:@//' + db_server_name + ':' + db_server_port + '/' + db_service;

# JDBC driver to be used for the STB Database connection
service_db_driver='oracle.jdbc.OracleDriver';

# ODI supervisor user
odi_supervisor='{{ supervisor_user }}';

# ODI Supervisor user's password
odi_supervisor_pass='{{ supervisor_password }}';

# ODI agent name for the Jee agent. Default teample contains OracleDIAgent
odi_instance='OracleDIAgent'; 

# Listen Address
odi_listen_address = '{{ server_hostname }}';

# ODI Port
odi_port = "8001";

# ODI Protocol
odi_protocol = "http";

# Agent Machine Name from template
agent_machine="LocalODIMachine";  

# Work repository name
odi_work_repository_name='{{ work_repository }}';



#Master Repository datasource name. Default is odiMasterRepository
master_db_datasource = "odiMasterRepository";

# master db definitions below are not needed here if they are coming from the service_db
#master_db_user="ENTERPRISE_ODI_REPO";
#master_db_pass="abc123";
#master_db_url="<master_db_url>"
#master_db_driver="<master_db_driver>"

#Work Reposiotry datasource name. Default is odiWorkRepository
work_db_datasource = "odiWorkRepository"; 

# work db definitions are not needed here if they are coming from the service_db
#work_db_user="<prefix>_ODI_REPO";
#work_db_pass="<work_db_password>";
#work_db_url="<work_db_url>"
#work_db_driver="<work_db_driver>"

########################################################################
#DO NOT MODIFY THE CODE BELOW THIS LINE
########################################################################

def createDataSource(dsName, user, password, url, driver):
	print 'Setting JDBCSystemResource with name '+dsName
	cd('/');
        existing=true;
        try:
		cd('/JDBCSystemResource/'+dsName+'/JdbcResource/'+dsName)
        except :
                existing=false;
	if ( not(existing) ) :
		create(dsName,'JDBCSystemResource');
	cd('/JDBCSystemResource/'+dsName+'/JdbcResource/'+dsName)
	if ( not(existing) ) :
		create('NO_NAME_0', 'JDBCDriverParams')
	cd('JDBCDriverParams/NO_NAME_0')
	cmo.setPasswordEncrypted(password)
	cmo.setUrl(url)
	cmo.setDriverName(driver)
	if ( not(existing) ) :
		create('NO_NAME_0', 'Properties')
	cd('Properties/NO_NAME_0');
	if ( not(existing) ) :
		create('user', 'Property')
	cd('Property/user')
	cmo.setValue(user)

def createWLSUser(user, password):
	cd(r'/Security/base_domain/User/'+user)
	cmo.setPassword(password)
	cd(r'/Server/AdminServer')
	cmo.setName('AdminServer')
	cd(r'/SecurityConfiguration/base_domain/')
	cmo.setNodeManagerUsername(user);
	cmo.setNodeManagerPasswordEncrypted(password);

def createODIInstance(instance, machine, listen_address, port, supervisor, supervisor_pass, datasource):
	cd('/');
        existing=true;
        try:
                cd('/SystemComponent/'+instance);
        except :
                existing=false;
        if( not(existing) ) :
		create(instance,"SystemComponent");
	cd('/SystemComponent/'+instance);
	set('ComponentType','ODI');
	set('Machine',machine);
	cd('/SystemCompConfig/OdiConfig/OdiInstance/'+instance);
	set("ListenAddress",listen_address);
	cmo.setListenPort(port);
	set('SupervisorUsername', supervisor);
	set('PasswordEncrypted', supervisor_pass);
	set('PreferredDataSource', datasource);

def makeOPSSChanges(supervisor, password):
        #OPSS related changes - START
        cd(r'/Credential/TargetStore/oracle.odi.credmap/TargetKey/SUPERVISOR')
        create('c','Credential')
        cd(r'Credential')
        cmo.setUsername(supervisor)
        cmo.setPassword(password)
        #OPSS related changes - END

##################################################################################

if not os.path.isdir(mw_home):
      sys.exit("Error: fusion middleware home directory '" + mw_home + "' does not exist.")

wls_domain_template_jar = "/wlserver/common/templates/wls/wls.jar"
wls_domain_creation_template_path = mw_home + wls_domain_template_jar

domain_path = wls_domain_dir + '/' + wls_domain_name

work_template_jar = '/common/templates/wls/odi_work_datasource_template.jar'
agent_template_jar = '/common/templates/wls/odi_agent_template.jar'
odi_cam_template_jar = '/common/templates/wls/odi_cam_managed_template.jar'

#reads the template jar for domain creation
readTemplate(wls_domain_creation_template_path, 'Compact')
createWLSUser(wls_user, wls_pass);

#extending ODI domain with all ODI templates
addTemplate(odi_oracle_home + work_template_jar) 
addTemplate(odi_oracle_home + agent_template_jar)
addTemplate(odi_oracle_home + odi_cam_template_jar)
cd('/SecurityConfiguration/base_domain') # domain is base_domain until saved as otherwise
cmo.setUseKSSForDemo(false)
makeOPSSChanges(odi_supervisor, odi_supervisor_pass);

#### Pre JDBC configuration to connect to the service_db database
createDataSource( 'LocalSvcTblDataSource', service_db_user, service_db_pass, service_db_url, service_db_driver);

#this section extends domain with ODI templates

# not needed if taking definitions from service_db
# createDataSource( master_db_datasource, master_db_user, master_db_pass, master_db_url, master_db_driver);

# not needed if taking definitions from service_db
#createDataSource( work_db_datasource, work_db_user, work_db_pass, work_db_url, work_db_driver);

# standalone-agent  (odi_cam_managed_template)

createODIInstance(odi_instance, agent_machine, odi_listen_address, odi_port, odi_supervisor, odi_supervisor_pass, master_db_datasource)

cd('/')
#create(agent_machine, 'Machine') # agent_machine == LocalOdiMachine, it exists in the template
cd('/Machine/'+agent_machine)
create(agent_machine, 'NodeManager')
cd('NodeManager/'+agent_machine)
cmo.setListenAddress(host_name)

# configure JEE agent from  the static template or a generated template
#cd('/Server/ODI_server1')
#cmo.setListenPort(8001) 


cd('/')
servers    = cmo.getServers()
for server in servers:
    sName = server.getName()
    cd('/Servers/' + sName)
    listenAddress = cmo.getListenAddress()
    if ( listenAddress == None or listenAddress == 'All Local Addresses') :
        cmo.setListenAddress(None)

getDatabaseDefaults(); # service_db, master_db, work_db (and opss) definitions from service_db

print "domain_path "+domain_path;
writeDomain(domain_path)
closeTemplate()
print '***************************************************************************************'
print 'Done creating ODI JEE Agent domain, Master repository, Supervisor user and Nodemanager'
print '***************************************************************************************'

exit()

