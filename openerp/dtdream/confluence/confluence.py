# -*- coding: utf-8 -*-
#!/usr/bin/python
"""Confluence XML-RPC Wrapper for Python"""


from xmlrpclib import Server
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ConfluenceServer(object):
    """This class is is used to create an object for interacting with a Confluence Wiki instance.
    
    Attributes:
        URL         Full URL for Confluence instance
        session     Shorthand for XML-RPC methods that start with confluence2
        token       Authentication token; mandatory for all operations.
        PDFsession  Shorthand for XML-RPC methods that start with pdfexport
    """
    def __init__(self,ConfluenceURL,login='',password=''):
        self.URL = ConfluenceURL
        logger.info("Establishing Connection to confluence at %s" % ConfluenceURL)
        self.session = Server(ConfluenceURL+'/rpc/xmlrpc').confluence2
        logger.info("Connection established. Logging in as %s" % login)
        self.token = self.session.login(login,password)
        logger.info("Successfully logged in as %s" % login)
        self.PDFsession = Server(ConfluenceURL+'/rpc/xmlrpc').pdfexport
        
    def GetLabelPages(self,label):
        """Get all pages associated with label"""
        return self.session.search(self.token,'labelText:%s and type:page' % label, 10000)
        
    def GetSpace(self,spacekey):
        """Get all page summaries (visible to current user) in spacekey"""
        return self.session.getSpace(self.token,spacekey)
        
    def AddPage(self,page):
        """Store a page. See https://developer.atlassian.com/display/CONFDEV/Remote+Confluence+Data+Objects#RemoteConfluenceDataObjects-pagePage for details."""
        return self.session.storePage(page)

    def DeletePage(self,pageId):
        """Delete a page"""
        return self.session.removePage(self.token,pageId)
        
    def ContentArray(self,articles):
        """Accepts the results of a search (such as GetLabelPages) and returns an array with the result of GetPage for each search result."""
        return [self.session.getPage(self.token,page['id']) for page in articles]

    def AddSpace(self,name,key,description):
        """Create a space"""
        space = {'key': key.rstrip(), 'name': name.rstrip(), 'description': description}
        return self.session.addSpace(self.token,space)

    def RemoveSpace(self,spacekey):
        """Delete a space"""
        return self.session.removeSpace(self.token,spacekey)
        
    def ExportSpace(self,space):
        """Perform a PDF Export of a space and return the download URL"""
        return self.PDFsession.exportSpace(self.token,space)
        
    def ListPageAttachments(self,pageId):
        """List all page attachments"""
        return self.session.getAttachments(self.token,pageId)
        
    def GetAttachment(self,pageId,fileName):
        """Get attachment Data"""
        return self.session.getAttachmentData(self.token,pageId,fileName,'0')
        
    def AddAttachment(self,pageId,attachmentDict,attachmentData):
        """Add Attachment -- attachmentDict info: https://developer.atlassian.com/display/CONFDEV/Remote+Confluence+Data+Objects#RemoteConfluenceDataObjects-attachmentAttachment """
        return self.session.addAttachment(self.token,pageId,attachmentDict,attachmentData)

    def CreateDuplicate(self,content,newSpace):
        """Duplicate a page (including attachments)"""
        copy = content.copy()
        [copy.pop(key) for key in ['id', 'parentId', 'title', 'space', 'version', 'modified']]
        formatAttributes = {'space': content['space'], 'id': content['id'], 'title': content['title']}
        copy['space'] = newSpace
        copy['title'] = "%s - %s - %s" % (content['space'].upper(), content['title'], content['id'])
        storedCopy = self.session.storePage(self.token,copy)
        for a in self.ListPageAttachments(content['id']):
            try:
                attachment = self.GetAttachment(content['id'],a['fileName'])
                self.AddAttachment(storedCopy['id'],{'fileName':a['fileName'],'contentType':a['contentType']},attachment)
            except:
                logger.error("Attachment %s from %s is missing from the content store" % (a['fileName'],content['title']))
                
    def GetSpacePages(self, spacekey):
        """Return summaries of all pages visible by the current user in a given space"""
        return self.session.getPages(self.token,spacekey)
            
    def GetRestrictions(self, pageId):
        """Return a list of permissions applied to the current page"""
        return self.session.getPagePermissions(self.token, str(pageId))
        
#    def SetRestrictons(self, pageId, permissionType, permissions=[]):
#        """ 
#        Replace restrictions on a page (blank=none)
#        WARNING! This will replace all permissions of the chosen type with the ones provided in the list!
#        Permission format is [{'userName':username1},{'userName':username2}] and so on.
#        """
#        return self.session.setPagePermissions(self.token, pageId, permissionType, permissions)
#        
#    def AddRestrictions(self, pageId, permissionType, entity):
#        perms = [p['lockedBy'] for p in self.GetRestrictions(pageId) if p['lockType'] == permissionType]
#        perms.append(entity)
#        
#        return [{'userName': e} for e in perms]
        #return self.session.setPagePermissions(self.token, pageId, permissionType, permissions = [{'userName': e} for e in perms]) 
        
    def GetSpaces(self):
        """Return summaries of all spaces visible to the current user"""
        return self.session.getSpaces(self.token)
        
    def GetSpacePermissionSets(self,spacekey):
        """Return permissions for a space"""
        return self.session.getSpacePermissionSets(self.token, spacekey)
    
    def GetSpacePermissionsForUser(self,spacekey,userName):
        """Return User's Permissions for a space"""
        return self.session.getPermissionsForUser(self.token, spacekey, userName)
        
    def GetSpacePermissionsForGroup(self,spacekey,group):
        """Return Group's Permissions for a space"""
        permissions = self.GetSpacePermissionSets(spacekey)
        groupPermissions = []
        for p in permissions:
            for q in p['spacePermissions']:
                if q.has_key('groupName'):
                    if q['groupName'] == group:
                        groupPermissions.append(q['type'])
        return groupPermissions
        
    def GrantPermissionsForSpace(self,entity,spacekey,permissions):
        """
        Grant a list of permissions to the user or group.
        Examples: https://developer.atlassian.com/confdev/confluence-rest-api/confluence-xml-rpc-and-soap-apis/remote-confluence-methods#RemoteConfluenceMethods-Permissions.1
        OR see the next method.
        """
        return self.session.addPermissionsToSpace(self.token,permissions,entity,spacekey)
        
    def RemovePermissionsForSpace(self,entity,spacekey,permissions=["VIEWPAGE","VIEWSPACE","EDITSPACE",
        "EXPORTPAGE","SETPAGEPERMISSIONS","REMOVEPAGE","EDITBLOG","REMOVEBLOG","COMMENT",   
        "REMOVECOMMENT","CREATEATTACHMENT","REMOVEATTACHMENT","REMOVEMAIL","EXPORTSPACE",
        "SETSPACEPERMISSIONS"]):
        """
        Remove a list of permissions for a user or group from a space (default is all)
        """
        results = {}
        for permission in permissions:
            results[permission] = self.session.removePermissionFromSpace(self.token,permission,entity,spacekey)
        return results
        
        
        
