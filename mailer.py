try:
    from freeswitch import *

except ImportError:
    pass

import smtplib
from os.path import basename, join
from os import getcwd, chdir
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from platform import python_version
from xml.etree import ElementTree as ET
from sys import version_info

if version_info.major == 3:
    Py3 = True
    Py2 = False

elif version_info.major == 2:
    Py3 = False
    Py2 = True
    
class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
        
class FaxSender(Singleton):
    
    def _parseXML(self):
        parsedContent = {}
        try:
            self.__receipientList

        except AttributeError:
            self.__receipientList = ET.parse(join(getcwd(), 'listconfig.xml')).getroot()

        parsedContent['username'] = self.__receipientList[0][0].text
        parsedContent['password'] = self.__receipientList[0][1].text
        parsedContent['host'] = self.__receipientList[0][2].text
        parsedContent['port'] = int(self.__receipientList[0][3].text)
        parsedContent['from'] = self.__receipientList[1].text

        for receivers in self.__receipientList[2].getchildren():
            if receivers.tag == 'receiverto':
                if len(receivers.getchildren()) > 0:
                    parsedContent['to'] = []

                    for toadd in receivers.getchildren():
                        parsedContent['to'].append(toadd.text)

            elif receivers.tag == 'receivercc':
                if len(receivers.getchildren()) > 0:
                    parsedContent['cc'] = []

                    for tocc in receivers.getchildren():
                        parsedContent['cc'].append(tocc.text)

            elif receivers.tag == 'receiverbcc':
                if len(receivers.getchildren()) > 0:
                    parsedContent['bcc'] = []

                    for tobcc in receivers.getchildren():
                        parsedContent['bcc'].append(tobcc.text)
        return parsedContent

    def _mailHandler(self, param):
        msg = MIMEMultipart()
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
        msg['Subject'] = content
        msg['From'] = param['parsedContent']['from']

        sender = param['parsedContent']['from']
        receiver = []

        if len(param['parsedContent']['to']) > 0:
            for tox in range(len(param['parsedContent']['to'])):
                if tox == 0:
                    msg['To'] = param['parsedContent']['to'][tox]

                else:
                    msg['To'] += ',' + param['parsedContent']['to'][tox]
                receiver.append(param['parsedContent']['to'][tox])
        if Py2:
            if param['parsedContent'].has_key('cc'):
                if len(param['parsedContent']['cc']) > 0:
                    for cxx in range(len(param['parsedContent']['cc'])):
                        if cxx == 0:
                            msg['Cc'] = param['parsedContent']['cc'][cxx]

                        else:
                            msg['Cc'] += ',' + param['parsedContent']['cc'][cxx]
                        receiver.append(param['parsedContent']['cc'][cxx])

            if param['parsedContent'].has_key('bcc'):
                if len(param['parsedContent']['bcc']) > 0:
                    for bccx in range(len(param['parsedContent']['bcc'])):
                        if bcxx == 0:
                            msg['Bcc'] = param['parsedContent']['bcc'][bccx]

                        else:
                            msg['Bcc'] += ',' + param['parsedContent']['bcc'][bccx]
                        receiver.append(param['parsedContent']['bcc'][bccx])

        elif Py3:
            if 'cc' in param['parsedContent']:
                if len(param['parsedContent']['cc']) > 0:
                    for cxx in range(len(param['parsedContent']['cc'])):
                        if cxx == 0:
                            msg['Cc'] = param['parsedContent']['cc'][cxx]

                        else:
                            msg['Cc'] += ',' + param['parsedContent']['cc'][cxx]
                        receiver.append(param['parsedContent']['cc'][cxx])

            if 'bcc' in param['parsedContent']:
                if len(param['parsedContent']['bcc']) > 0:
                    for bccx in range(len(param['parsedContent']['bcc'])):
                        if bcxx == 0:
                            msg['Bcc'] = param['parsedContent']['bcc'][bccx]

                        else:
                            msg['Bcc'] += ',' + param['parsedContent']['bcc'][bccx]
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

        msg.attach(MIMEText(content, 'plain'))
        msg.attach(pdfpart)
        if tiffile is not None:
            msg.attach(tiffpart)

        # msg.attach(MIMEText(html,'html'))

        user = param['parsedContent']['username']
        password = param['parsedContent']['password']
        smtps = smtplib.SMTP(param['parsedContent']['host'], param['parsedContent']['port'])
        smtps.starttls()
        smtps.login(user, password)

        smtps.sendmail(sender, receiver, msg.as_string())

    def callRoutine(self, caller, pdffile, tiffile=None):
        parsedContent = self._parseXML()
        self._mailHandler({
            'parsedContent': parsedContent,
            'caller': caller,
            'pdffile': pdffile,
            'tiffile': tiffile
        })

def fsapi(session, stream, env, args):
    if getcwd() != '/usr/local/src/fs':
        chdir('/usr/local/src/fs')
    
    stream.write("hello I am in this path: {} \n".format(getcwd()))
    stream.write("And I am Python Version: {}".format(python_version()))

    FSenderObj = FaxSender()
    FSenderObj.callRoutine(
        session.getVariable("caller"),
        session.getVariable("pdffile"),
        session.getVariable("tiffile")
    )

def handler(session, args):
    pass

if __name__ == '__main__':
    fs = FaxSender()
    fs.callRoutine('053122434811', '/var/spool/spandsp/d261da70-a74b-435c-9574-90bc40e66e8e.pdf', None)
