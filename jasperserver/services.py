# -*- coding: utf-8 -*-
##############################################################################
#
#    jasperserver library module for OpenERP
#    Copyright (C) 2012 SYLEAM ([http://www.syleam.fr]) Christophe CHAUVET
#
#    This file is a part of jasperserver library
#
#    jasperserver library is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    jasperserver library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see [http://www.gnu.org/licenses/].
#
##############################################################################
from resourcedescriptor import *
import os
from StringIO import StringIO


try:
    from lxml import etree
except ImportError:
    import xml.etree.cElementTree as etree


class Resources (object):
    '''
    an Resources instance implements resources service in JasperServer. You need an open session js_connect to use this service.
    the path is the URI to browse. This class implements resources service in JasperServer.
    You need an open session *js_connect* to use this service.
    *path* is the URI to browse.
    '''

    def __init__(self, js_connect, path=''):
        self._connect = js_connect
        self.path = path
        self.url = js_connect._rest_url + '/resources' + path

    def search(self, description='', wstype='', recursive='0', item_max='0'):
        '''
        Browse the path. When used without arguments, it gives the list of resources in the folder specified in the URL.
        With the arguments, you can search for terms in the resource names or descriptions, search for all resources of a given *wstype*, and specify whether to search in subfolders.
        The *recursive* parameter is only used if a search criteria is specified (either *q* or *wstype*).
        This method return each found resource : name, type and uri in a dictionnary.
        '''
        params = {'q': description,
             'type': wstype,
             'recursive': recursive,
             'limit': item_max
        }
        xml = self._connect.get(self.url, params=params)
        res = []
        if xml:
            tree = etree.XML(xml)
            for name in tree.findall('resourceDescriptor'):
                r = {}
                r['name'] = name.get('name')
                r['wsType'] = name.get('wsType')
                r['uriString'] = name.get('uriString')
                res.append(r)

        return res


class Resource (object):
    '''
    an Resource instance implements resource service in JasperServer. you need an open session js_connect to use this service. *path* is the folder where methods will be used.
    '''

    def __init__(self, js_connect, path=''):
        self._connect = js_connect
        self.path = path
        self.url = js_connect._rest_url + '/resource/'

    def create(self, resource_name, wsType, path_fileresource='',
               uri_datasource='/datasources/openerp_demo', uri_jrxmlfile='',
               jdbc_username='', jdbc_password='', jdbc_url='', jdbc_driver='org.postgresql.Driver'):
        '''
        Create a simple resource or a resource with an attached file.
        *wsType* : type of the resource (see jasper web service documentation).
        If you send a file resource, you need an *uri_jrxmlfile*.
        '''
        url = ''
        hasData = False
        if path_fileresource:
            hasData = True

        rd, uri = self.build_resourceDescriptor(resource_name=resource_name, wsType=wsType, hasData=hasData,
                                           uri_datasource=uri_datasource, uri_jrxmlfile=uri_jrxmlfile,
                                           jdbc_username=jdbc_username, jdbc_password=jdbc_password, jdbc_url=jdbc_url,
                                           jdbc_driver=jdbc_driver)
        url = self.url + self.path
        return self._connect.put(url, data=rd, files=path_fileresource, uri=uri)

    def modify(self, resource_name, wsType, path_fileresource=None,
               uri_datasource='/datasources/openerp_demo', uri_jrxmlfile='',
               jdbc_username='', jdbc_password='', jdbc_url='', jdbc_driver='org.postgresql.Driver'):
        '''
        Modify a simple resource or a resource with an attached file.
        *wsType* : type of the resource (see jasper web service documentation).
        If you send a file resource, you need an *uri_jrxmlfile*.
        '''
        url = ''
        hasData = False
        if path_fileresource:
            hasData = True

        rd, uri = self.build_resourceDescriptor(resource_name=resource_name, wsType=wsType, hasData=hasData,
                                           uri_datasource=uri_datasource, uri_jrxmlfile=uri_jrxmlfile,
                                           jdbc_username=jdbc_username, jdbc_password=jdbc_password, jdbc_url=jdbc_url,
                                           jdbc_driver=jdbc_driver)

        url = self.url + uri
        return self._connect.post(url, data=rd, files=path_fileresource, uri=uri)

    def get(self, resource_name, fileid=None, uri_datasource=None, param_p=None, param_pl=None):
        '''
        Request the content of the resource
        This method is used to show the information about a specific resource. Getting a resource can serve several purposes: In the case of JasperReports, also known as report units, this service returns the structure of the JasperReport, including resourceDescriptors for any linked resources. Specifying a JasperReport and a file identifier returns the file itself. Specifying a query-based input control with arguments for running the query returns the dynamic values for the control.
        Return the binary content.
        '''
        params = {}
        if fileid:
            params['file'] = fileid

        if uri_datasource:
            params['IC_GET_QUERY_DATA'] = uri_datasource

            if param_p:
                params['param_p'] = param_p

            if param_pl:
                params['param_pl'] = param_pl

        url = self.url + self.path + '/' + resource_name
        return self._connect.get(url, params=params)

    def delete(self, resource_name):
        '''
        Delete a resource in the current path
        '''
        urltodelete = self.url + self.path + '/' + resource_name
        self._connect.delete(urltodelete)

    def build_resourceDescriptor(self, resource_name, wsType, hasData=False,
                                 uri_datasource='/datasources/openerp_demo', uri_jrxmlfile='',
                                 jdbc_username='', jdbc_password='', jdbc_url='',
                                 jdbc_driver='org.postgresql.Driver'):
        # Build the resource descriptor in resourceDescriptor tags XML
        # Returns a tuple with the string of the resourceDescriptor, and the uri of the file resource.
        uri = self.path + '/' + resource_name

        rd = ResourceDescriptor(name=resource_name, wsType=wsType, uriString=uri)
        rd.append(Label(resource_name))
        rd.append(ResourceProperty('PROP_PARENT_FOLDER', self.path))
        if hasData:
            rd.append(ResourceProperty('PROP_HAS_DATA', 'true'))

        if wsType == 'reportUnit':
            rd.append(ResourceProperty('PROP_RU_ALWAYS_PROPMT_CONTROLS', 'true'))
            rd.append(ResourceProperty('PROP_RU_CONTROLS_LAYOUT', '1'))
            rdds = ResourceDescriptor(wsType='datasource')
            rdds.append(ResourceProperty('PROP_REFERENCE_URI', uri_datasource))
            rdds.append(ResourceProperty('PROP_IS_REFERENCE', 'true'))
            rd.append(rdds)
            rdjrxml = ResourceDescriptor(name=resource_name, wsType='jrxml')
            rdjrxml.append(ResourceProperty('PROP_IS_REFERENCE', 'true'))
            rdjrxml.append(ResourceProperty('PROP_REFERENCE_URI', uri_jrxmlfile + '/' + resource_name ))
            rdjrxml.append(ResourceProperty('PROP_RU_IS_MAIN_REPORT', 'true'))
            rd.append(rdjrxml)

        if wsType == 'jdbc':
            rd.append(ResourceProperty('PROP_DATASOURCE_DRIVER_CLASS', driverClass))
            rd.append(ResourceProperty('PROP_DATASOURCE_USERNAME', ds_username))
            rd.append(ResourceProperty('PROP_DATASOURCE_PASSWORD', ds_password))
            rd.append(ResourceProperty('PROP_DATASOURCE_CONNECTION_URL', ds_url))

        prettyrd = etree.tostring(rd, pretty_print=True)
        return prettyrd, uri


class Report(object):
    '''
    This class implements the new rest_v2 service, only for running a report in the reports units path.
    '''

    def __init__(self, js_connect, path):
        self._connect = js_connect
        self.url = js_connect._rest_url + '_v2/reports' + path + '/'

    def run(self, name, output_format='pdf', page='', onepagepersheet=''):
        '''
        Create a report with rest_V2 service. you can export a specific *page* and select one page per sheet if you choose an XLS format.
        Return the binary content.
        '''
        params = None
        if page:
            params = {'page': page}
        if onepagepersheet:
            params['onePagePerSheet'] = onepagepersheet

        return self._connect.get(self.url + name + '.' + output_format, params=params)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
