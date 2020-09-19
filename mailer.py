try:
    from freeswitch import *
    
except ImportError:
    pass

import smtplib
from os.path import basename,join
from os import getcwd,chdir
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from platform import python_version
from sys import version_info
from xml.etree import ElementTree as ET
from additional import Py2,Py3, Singleton


class FaxSender(Singleton):
    def __init__(self,confpath):
        self.__confPath = confpath
        
        try:
            self.__msg
            
        except AttributeError:
            self.__msg = MIMEMultipart()    
    
    def _parseXML(self):
        parsedContent = {}
        try:
            self.__receipientList
            
        except AttributeError:
            self.__receipientList = ET.parse(join(self.__confPath,'listconfig.xml')).getroot()
        
        parsedContent['username'] = self.__receipientList[0][0].text
        parsedContent['password'] = self.__receipientList[0][1].text
        parsedContent['host'] = self.__receipientList[0][2].text
        parsedContent['port'] = int(self.__receipientList[0][3].text)
        parsedContent['from'] = self.__receipientList[1].text
        
        for receivers in self.__receipientList[2].getchildren():
            if receivers.tag == 'receiverto':
                if len(receivers.getchildren())>0:
                    parsedContent['to'] = []
                    
                    for toadd in receivers.getchildren():
                        parsedContent['to'].append(toadd.text)
            
            elif receivers.tag == 'receivercc':
                if len(receivers.getchildren())>0:
                    parsedContent['cc'] = []
                    
                    for tocc in receivers.getchildren():
                        parsedContent['cc'].append(tocc.text)
            
            elif receivers.tag == 'receiverbcc':
                if len(receivers.getchildren())>0:
                    parsedContent['bcc'] = []
                    
                    for tobcc in receivers.getchildren():
                        parsedContent['bcc'].append(tobcc.text)
                
        return parsedContent
        
    def _mailHandler(self,param):
        try:
            self.__msg
        
        except AttributeError:
            self.__msg = MIMEMultipart()
            
        pdffile = param['pdffile']
        tiffile = param['tiffile']
        
        with open(pdffile, 'rb') as f:
            pdfpart = MIMEApplication(f.read(), Name=basename(pdffile))
        
        if tiffile is not None:            
            with open(tiffile, 'rb') as f:
                tiffpart = MIMEApplication(f.read(), Name=basename(tiffile))
            
        pdfpart['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(pdffile))
        if tiffile is not None:
            tiffpart['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(tiffile))
        
        source_number = param['caller']
        content = 'This Fax is from {}'.format(source_number)
        self.__msg['Subject'] = content
        self.__msg['From'] = param['parsedContent']['from']
        
        sender = param['parsedContent']['from']
        receiver = []
        
        if len(param['parsedContent']['to'])>0:            
            for tox in range(len(param['parsedContent']['to'])):
                if tox == 0:                    
                    self.__msg['To'] = param['parsedContent']['to'][tox]
                
                else:
                    self.__msg['To']+=','+param['parsedContent']['to'][tox]
                receiver.append(param['parsedContent']['to'][tox])
        if Py2:
            if param['parsedContent'].has_key('cc'):
                if len(param['parsedContent']['cc'])>0:
                    for cxx in range(len(param['parsedContent']['cc'])):
                        if cxx == 0:
                            self.__msg['Cc'] = param['parsedContent']['cc'][cxx]
                        
                        else:
                            self.__msg['Cc']+=','+param['parsedContent']['cc'][cxx]
                        receiver.append(param['parsedContent']['cc'][cxx])
                            
            if param['parsedContent'].has_key('bcc'):
                if len(param['parsedContent']['bcc'])>0:
                    for bccx in range(len(param['parsedContent']['bcc'])):
                        if bcxx == 0:
                            self.__msg['Bcc'] = param['parsedContent']['bcc'][bccx]
                        
                        else:                    
                            self.__msg['Bcc']+=','+param['parsedContent']['bcc'][bccx]
                        receiver.append(param['parsedContent']['bcc'][bccx])
                        
        elif Py3:
            if 'cc' in param['parsedContent']:
                if len(param['parsedContent']['cc'])>0:
                    for cxx in range(len(param['parsedContent']['cc'])):
                        if cxx == 0:
                            self.__msg['Cc'] = param['parsedContent']['cc'][cxx]
                        
                        else:
                            self.__msg['Cc']+=','+param['parsedContent']['cc'][cxx]
                        receiver.append(param['parsedContent']['cc'][cxx])
                            
            if 'bcc' in param['parsedContent']:
                if len(param['parsedContent']['bcc'])>0:
                    for bccx in range(len(param['parsedContent']['bcc'])):
                        if bcxx == 0:
                            self.__msg['Bcc'] = param['parsedContent']['bcc'][bccx]
                        
                        else:                    
                            self.__msg['Bcc']+=','+param['parsedContent']['bcc'][bccx]
                        receiver.append(param['parsedContent']['bcc'][bccx])            
            
        
        html = """\
        <html>
          <head></head>
          <body>
            <p>{}</p>
          </body>
        </html>
        """.format(content)
        ptext = content
        
        self.__msg.attach(MIMEText(content,'plain'))
        self.__msg.attach(pdfpart)
        if tiffile is not None:
            self.__msg.attach(tiffpart)
            
        #msg.attach(MIMEText(html,'html'))
        
        user = param['parsedContent']['username']
        password = param['parsedContent']['password']
        smtps = smtplib.SMTP(param['parsedContent']['host'],param['parsedContent']['port'])
        smtps.starttls()
        smtps.login(user,password)
        
        smtps.sendmail(sender, receiver, self.__msg.as_string())
        
    
    def callRoutine(self,caller,pdffile,tiffile=None):
        self.__targetno = caller
        self.__uuid = pdffile
        
        parsedContent = self._parseXML()
        self._mailHandler({
            'parsedContent':parsedContent,
            'caller':caller,
            'pdffile':pdffile,
            'tiffile':tiffile
        })

def fsapi(session, stream, env, args):    
    #FaxSender().callRoutine(None,None)
    stream.write("hello I am in this path: {} \n".format(getcwd()))
    stream.write("And I am Python Version: {}".format(python_version()))
    
def handler(session,args):
    cpath = '/usr/local/src/fs'
    FSenderObj = FaxSender(confpath=cpath)
    
    callerID = session.getVariable("caller")
    pdfFile = session.getVariable("pdffile")
    tiffFile = session.getVariable("tiffile")
    
    if tiffFile == '':
        tiffFile = None
    
    FSenderObj.callRoutine(
        callerID,
        pdfFile,
        tiffFile
    )
    
if __name__ == '__main__':    
    cpath='/usr/local/src/fs'
    FaxSender(confpath=cpath).callRoutine('053122434811','/var/spool/spandsp/d261da70-a74b-435c-9574-90bc40e66e8e.pdf',None)