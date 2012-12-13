import sys
from jasperserver.rest import Client
from jasperserver.admin import User
from jasperserver.repository import Resource
from jasperserver.repository import Resources
from jasperserver.exceptions import JsException
from jasperserver.report import Reportv2
from jasperserver.report import Report

try:
    client = Client('http://localhost:8080/jasperserver', 'jasperadmin', 'jasperadmin')
except JsException:
    print 'Error Authentification FAIL!'
    sys.exit(1)


try:
    # Must return a list with one record
    print '\n#######################\n'
    User(client).search('joeuser')
    print '\n#######################\n'
    Resources(client).search('openerp_demo')
except JsException:
    print 'Error when send user query'
    sys.exit(1)

try:
    resource1 = Resource(client,
                        '/openerp/bases/openerp_demo'
    )
    print '\n#######################\n'
    resource1.create('$YOURPATH/JasperServer-Library/template/examplefolder_resource.xml',
    #                '$YOURPATH/reportname.jrxml'
    )
    print '\n#######################\n'
    #Reportv2 use REST-v2 report Service
    report1 = Reportv2(client, '/openerp/bases/openerp_demo')
    #Report use REST report Service
    report2 = Report(client, '/openerp/bases/openerp_demo')

    name = raw_input('nom du report: ')
    if name == 'exit':
        print 'sortie du programme'
        sys.exit()
    extension = raw_input('format du fichier (par exemple: pdf): ')
    report1.run(name, extension)
    
    print '\n#######################\n'
    nametodelete = raw_input('Nom du rapport a supprimer : ')
    resource1.delete (nametodelete)
    
    name = raw_input('nom du report2: ')
    if name == 'exit':
        print 'sortie du programme'
        sys.exit()
    report2.run(name)
    print '\n#######################\n'

except:
    print "ERREUR"
    sys.exit(1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: