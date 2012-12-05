import urllib
import webapp2
from webapp2_extras.appengine.users import *
from google.appengine.ext import blobstore,db
from google.appengine.ext.blobstore import BlobInfo
from google.appengine.ext.webapp import blobstore_handlers
# from google.appengine.api import users

class FileRecord(db.Model):
  blob = blobstore.BlobReferenceProperty()
  
class MainHandler(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    respond = self.response.out.write
    upload_url = blobstore.create_upload_url('/upload')
    page = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "DTD/xhtml1-transitional.dtd">'
    page += '<html><head>'
    page += '<title>RSa file services</title>'
    page += '<link type="text/css" rel="stylesheet" href="/css/main.css" />'
    page += "<link href='http://fonts.googleapis.com/css?family=Open+Sans&subset=latin,cyrillic' rel='stylesheet' type='text/css'>"
    page += '</head><body>'
    page += '<h2><a href="http://appengine.google.com/dashboard?&app_id=s~rsa-host">RSa file services</a></h2>'
    if user:
      page += 'Welcome, %s! (<a href=\"%s\">sign out</a>)<p>' % (user.nickname(), users.create_logout_url("/"))
    else:
      page += 'Welcome, guest! (<a href=\"%s\"> Sign in or register</a>)<p>' % (users.create_login_url("/"))
    if users.is_current_user_admin(): 
      files = FileRecord.all()
      if files.count():
        page += '<table id="filelist">'
        page += '<tr><th>File Name</th><th>Size</th><th>MD5 hash</th><th>Uploaded</th><th>Delete?</th></tr>'      
        for record in files:
          date = record.blob.creation
          strdate = date.strftime("%Y-%m-%d %H:%M")
          key = record.key().id()
          filename = record.blob.filename
          size = '  ' + str(round(float(record.blob.size) / 1024 / 1024,3)) + ' Mb   '
          md5 = '  ' + str(record.blob.md5_hash) + '   '
          page += '<tr>'
          page += '<td><a href="/get/%s">%s</a></td>' % (key,filename)
          page += '<td>%s</td><td>%s</td><td>%s</td>' % (size,md5,strdate)
          page += '<td><a href="/delete/%s">Delete</a></td>' % (key)
          page += '</tr>'
        page += '</table><br>'
    page += '<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url
    page += 'Upload File: <input type="file" name="file">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="submit" name="submit" value="Submit">'
    #page += '<div id="footer">'
    #page += '<a href="http://code.google.com/appengine/"><img src="http://code.google.com/appengine/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine" /></a>'
    #page += '</div>'
    page += '</body></html>'
    respond(page)

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    blob_info = self.get_uploads('file')[0]
    record = FileRecord(blob = blob_info)
    record.put()
    self.redirect('/')

class GetHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, blob_key):
    blob_key = str(urllib.unquote(blob_key))
    record = FileRecord.get_by_id(int(blob_key))
    self.send_blob(record.blob,save_as=record.blob.filename)
    
class DeleteHandler(webapp2.RequestHandler):
  def get(self,blob_key):
    try:
      blob_key = urllib.unquote(blob_key)
      record = FileRecord.get_by_id(int(blob_key))
      
      record.blob.delete()
      record.delete()
    except:
      self.error(404)
    self.redirect('/')

app = webapp2.WSGIApplication(
          [('/', MainHandler),
           ('/upload', UploadHandler),
           ('/delete/([^/]+)?', DeleteHandler),
           ('/get/([^/]+)?', GetHandler),
          ], debug=False)
