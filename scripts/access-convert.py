#!  /usr/bin/env python3
# This software is Copyright (C) 2020 The Regents of the University of
# California. All Rights Reserved. Permission to copy, modify, and
# distribute this software and its documentation for educational, research
# and non-profit purposes, without fee, and without a written agreement is
# hereby granted, provided that the above copyright notice, this paragraph
# and the following three paragraphs appear in all copies. Permission to
# make commercial use of this software may be obtained by contacting:
#
# Office of Innovation and Commercialization
#
# 9500 Gilman Drive, Mail Code 0910
#
# University of California
#
# La Jolla, CA 92093-0910
#
# (858) 534-5815
#
# invent@ucsd.edu
#
# This software program and documentation are copyrighted by The Regents of
# the University of California. The software program and documentation are
# supplied "as is", without any accompanying services from The Regents. The
# Regents does not warrant that the operation of the program will be
# uninterrupted or error-free. The end-user understands that the program
# was developed for research purposes and is advised not to rely
# exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES,
# INCLUDING LOST PR OFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS
# DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY
# DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
# SOFTWARE PROVIDED HEREUNDER IS ON AN "AS IS" BASIS, AND THE UNIVERSITY OF
# CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
# ENHANCEMENTS, OR MODIFICATIONS.
__author__ = "Bradley Huffaker"
__email__ = "<bradley@caida.org>"
import argparse
import json
import sys
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="+", type=str, help="single json object file")
args = parser.parse_args()

re_json = re.compile("json$")
re_markdown = re.compile("md$")
re_id_illegal = re.compile("[^\d^a-z^A-Z]+")
re_type_id = re.compile("[^\:]+:(.+)")

def main():
    re_start = re.compile('^\s*"resources":\s*\[')
    re_end = re.compile('^\s*\],$')
    match = False
    for fname in args.files:
        #print (fname)
        with open (fname) as fin:
            obj = None
            state = "before"
            content = {
                "before":"",
                "after":""
            }
            r_buffer = None
            for line in fin:
                if state == "during":
                    if re_end.search(line):
                        r_buffer += "]}"
                        obj = obj_update(r_buffer)
                        encoded = "\n".join(json.dumps(obj,indent=4).split("\n")[1:-1])+",\n"
                        content["resources"] = encoded
                        state = "after"
                    else:
                        r_buffer += line
                elif obj is None and re_start.search(line):
                    r_buffer = '{"resources":['
                    state = "during"
                else:
                    content[state] += line
            fin.close()
            fout = sys.stdout
            if "resources" in content:
                for state in ["before","resources","after"]:
                    fout.write(content[state])

def obj_update(text):
    obj = json.loads(text)
    if "resources" in obj:
        resources = []
        accesses = []
        for resource in obj["resources"]:
            if resource["name"] == "public" or resource["name"] == "restricted" or resource["name"] == "commercial":
                resource["access"] = resource["name"]
                resource.pop('name', None)
                accesses.append(resource)
            elif resource["name"] == "PDF" or resource["name"] == "web page":
                resource["access"] = "public"
                resource["tags"] = [resource["name"]]
                resource.pop('name', None)
                accesses.append(resource)
            elif resource["name"].lower() == "video":
                resource["access"] = "public"
                resource["tags"] = ["video"]
                resource.pop('name', None)
                accesses.append(resource)
            elif resource["name"][:3] == "PNG" or resource["name"][:3] == "GIF":
                resource["access"] = "public"
                resource["tags"] = [resource["name"][:3]]
                if len(resource["name"]) == 3:
                    resource.pop('name', None)
                accesses.append(resource)
            else:
                resources.append(resource)
        if len(resources) > 0:
            obj["resources"] = resources
        else:
            obj.pop("resources",None)
        if len(accesses):
            obj["access"] = accesses
        return obj
    return None

main()
