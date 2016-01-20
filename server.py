#!/usr/bin/env python3.3

import http.server
import socketserver
import logging
import cgi
import os
import auths
import json
import os.path

with open("config.json") as file:
    config = json.load(file)

PORT = config["port"]


class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = '/upload.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        try:
            print("POST STARTED")
            print(self.headers)
            form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                             'CONTENT_TYPE': self.headers['Content-Type'],
                             })
            print("POST VALUES")
            for data in form:
                if type(form.getfirst(data)) is not bytes:
                    print(data + ":" + form.getfirst(data))

            keymatch = False
            if form.__contains__("key"):
                key = form.getfirst("key")
                keymatch = auths.chechPass(key)

            usecustomname = False
            customname = ""
            if form.__contains__("fname"):
                customname = form.getfirst("fname")
                usecustomname = True
                split = customname.split(".")
                length = len(split)
                if length is not 1:
                    extention = split[length - 1]
                    length = len(split)
                    customname = customname[:-(len(extention) + 1)]

                print("Custom file name: " + customname)

            customoutput = ""
            if form.__contains__("output"):
                customoutput = form.getfirst("output")

            if keymatch is True:
                print("Key valid. Receiving file")
            else:
                print("Key invalid. Ignoring file")

            hasfile = True
            fn = ""
            validfilename = True
            if form.__contains__("file") and keymatch is True:
                fileitem = form["file"]
                if fileitem.filename:
                    fn = os.path.basename(fileitem.filename)
                    split = fn.split(".")
                    length = len(split)
                    extention = split[length - 1]
                    if usecustomname is True:
                        filename = customname
                    else:
                        filename = fn[:-(len(extention) + 1)]
                    print("Filename: " + filename + " Extension: " + str(extention))
                    fileexists = True
                    fn = filename + "." + str(extention)
                    try:
                        newfile = open(config["filedir"] + fn)

                    except FileNotFoundError:
                        fileexists = False
                    except OSError:
                        validfilename = False

                    if fileexists and validfilename:
                        inc = 1
                        orig = fn
                        while (fileexists):
                            fn = filename + str(inc) + "." + str(extention)
                            try:
                                newfile = open(config["filedir"] + fn)

                            except FileNotFoundError:
                                fileexists = False

                            if fileexists:
                                inc += 1

                            else:
                                os.makedirs(os.path.dirname(config["filedir"] + fn), exist_ok=True)
                                open(config["filedir"] + fn, 'wb').write(fileitem.file.read())

                        message = 'The file "' + fn + '" was uploaded successfully'
                    elif validfilename:
                        os.makedirs(os.path.dirname(config["filedir"] + fn), exist_ok=True)
                        open(config["filedir"] + fn, 'wb').write(fileitem.file.read())

                        message = 'The file "' + fn + '" was uploaded successfully'
                    else:
                        message = "Invalid file name"

                else:
                    message = 'No file was uploaded'
                    hasfile = False

                print(message)
            else:
                hasfile = False

            print("\n")

            response = ""

            error = True

            self.send_response(200)
            if customoutput == "html":
                self.send_header("Content-type", "text/html")
                if keymatch is False:
                    response = ("<html><head><title>Upload Failed></title></head>"
                        "<body><p>Upload Failed: Invalid key</body></html>")
                elif hasfile is False:
                    response = ("<html><head><title>Upload Failed></title></head>"
                        "<body><p>Upload Failed: No file uploaded</body></html>")
                elif validfilename is False:
                    response = ("<html><head><title>Upload Failed></title></head>"
                    "<body><p>Upload Failed: Invalid file name</body></html>")
                else:
                    error = False
                    response = ("<html><head><title>Upload Complete></title></head>"
                        "<body><p>Upload Complete: <a href=\"" + config["host"] + fn + "\">" +
                        config["host"] + fn + "</a></body></html>")
            else:
                if keymatch is False:
                    response = '{\n    "success":false,\n    "error":"invalid key"\n}'
                elif hasfile is False:
                    response = '{\n    "success":false,\n    "error":"no file uploaded"\n}'
                elif validfilename is False:
                    response = '{\n    "success":false,\n    "error":"invalid file name"\n}'
                else:
                    error = False
                    response = '{\n    "success":true,\n    "url":"' + config["host"] + fn + '"\n}'

            self.end_headers()
            self.wfile.write(bytes(response, 'utf-8'))
        except RuntimeError:
            pass

Handler = ServerHandler

httpd = socketserver.TCPServer(("", PORT), Handler)

httpd.serve_forever()
