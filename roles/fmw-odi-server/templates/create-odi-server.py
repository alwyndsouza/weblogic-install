ADMIN_SERVER_URL = 't3://' + '{{ admin_server_hostname }}' + ':' + '{{ admin_server_port }}';

connect('{{ weblogic_admin }}', '{{ weblogic_admin_pass }}', ADMIN_SERVER_URL);

edit();
startEdit();

cd('/')
#machines = cmo.getMachines()
#servers = cmo.getServers()
cmo.createMachine('{{ server_hostname }}')

cd('/Machines/' + '{{ server_hostname }}' + '/NodeManager/' + '{{ server_hostname }}')
cmo.setListenAddress('{{ node_manager_listen_address }}')

cd('/')
#cmo.createServer('{{ odi_server_name }}')

cd('/Servers/' + '{{ odi_server_name }}')
cmo.setListenAddress('{{ server_hostname }}')
cmo.setListenPort({{ odi_server_port }})
cmo.setMachine(getMBean('/Machines/' + '{{ server_hostname }}'))
applyJRF(target='{{ odi_server_name }}', domainDir='{{ domain_home }}');

# applyJRF wil call save and activate
#save();
#activate(block='true');
disconnect();
