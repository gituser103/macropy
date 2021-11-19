import re, string,os, sys

# global data definitions start here

# put tokens you are searching for in a python dictionary
# which acts as a database
# tokens have attributes
macrodb = dict()
# 
# macroNameStack = []
pushback = ""
eofind = False
msgHeader = '\nmacro.py *debug* '
processComplete = False
ipfstack = []
fnamestack = []

macrodefpatt = re.compile('^([ ])*(#define).*')
txpatt = re.compile('[a-zA-Z0-9_]')
pattInclude = re.compile('^#[\t ]*include[\t ]+["]([a-zA-Z0-9_/\.]+)["]')
pattDefine =  re.compile('^#[\t ]*define[\t ]+([a-zA-Z0-9_]+)[\t ]*(.*)$')

def matchDelim(tok):
  if tok == '(':
     return ')'
  if tok == '[':
     return ']'
  if tok == '{':
     return '}'
  return ''

def iscontinued(token):
  tok = token.strip()
  if tok == '\\':
     return True
  if tok == ',':
     return True
  return False

def getfile(filename):
    global ipfstack
    global fnamestack
    global eofind
    global msgHeader
    if fnamestack.count(filename) > 0:
        print(msgHeader,'circular include for ', filename)
        return False
    if not os.path.exists(filename):
        print(msgHeader,'file not found ', filename)
        return False
    if not os.access(filename, os.R_OK):
        print(msgHeader,'file not readable ', filename)
        return False
    ipf = open(filename, 'r')
    ipfstack.append(ipf)
    fnamestack.append(filename)
    eofind = False
    return True


def read_file(ipf):
  global pushback
  global eofind
  if len(pushback) > 0:
     w_l = pushback
     pushback = ""
     return w_l
  if eofind:
     return ""
  w_l = ipf.readline()  
  if not w_l:
     eofind = True
     return "" 
  return w_l

def get_line(ipf):
  global eofind
  global pushback
  lastchar = ""   # terminating line character
  p_l = read_file(ipf)
  if not p_l:
    return ""
  if len(p_l) < 2:
    return p_l
#  p_l = p_l.rstrip('\r\n  ')
#  if not p_l:        # space line
#    return " \n" 
# iterate collecting input lines to a string buffer
  rawline = p_l       # rawline is our string buffer
  lastchar = rawline[-2]
  while not eofind and iscontinued(lastchar):
   p_l = read_file(ipf)
   if p_l:
     isMacro = macrodefpatt.match(p_l)
     if isMacro:
       pushback = p_l        #  we have read too far
#       rawline[-2] = " "       #  fix erroneous last char
#       rawline = rawline + '\n'
       rawline = rawline[:-2] + " \n"
       lastchar = " "
     else:
       rawline = rawline + p_l
       lastchar = rawline[-2]
# do not return a continuation line
  if iscontinued(rawline[-2]):
       rawline = rawline[:-2] + " "
#      rawline[-2] = " "
#      rawline = rawline + '\n'
  return rawline


def isquote(character):
    if character == "0x22":
        return 1
    if character == "0x27":
        return 1
    return 0
    
def trieSearch(searchlist):
    # finds longest match
    # searcharray[0] is the search field you are trying to match
    # searcharray[1:] is a list of candidate matches
    # will return:-
    #  an exact match for searcharray[0]
    #  or the longest element in searcharray[1:]
    #  that starts the search field

    if len(searchlist) < 2:
        return []
# too few arguments

    list1 = searchlist
    list1_0_len = len(list1[0])
    lenlist1 = [list1_0_len]  # element zero is a constant
    for listindex in range(1, len(list1)):
        lenlist1.append(len(list1[listindex])) # build list of lengths
    # list of lenths of corresponding elements in list1
    found = []  # accumulate matches by string length
    characterIndex = 0

    # searchlist[0] is the item you are seeking to match
    # searchlist[1:] is the list of possible matches

    while (len(list1) > 1) and (characterIndex < list1_0_len):
        list2 = [list1[0]]
        lenlist2 = [list1_0_len]
        while list1_0_len > characterIndex:
            # characterIndex iterates over chars to be matched

            # list2 is the output from the search pass
            # at the end of each pass list2 is copied to list1

            for listindex in range(1, len(list1)):
                # listindex iterates over fields to be matched
                if (lenlist1[listindex] > characterIndex) and (list1_0_len > characterIndex):
                    # if lengths are in range
                    if list1[0][characterIndex] == list1[listindex][
                            characterIndex]:
                        # and corresponding chars match for this pass
                        list2.append(list1[listindex])
                        lenlist2.append(lenlist1[listindex])
# list2 has matches for this pass
#                list2 is a list of matches for the latest pass

            list1 = list2
            lenlist1 = lenlist2
            list2 = [list1[0]]
            lenlist2 = [list1_0_len]
            characterIndex = characterIndex + 1
            # iterate over list1[1] - list1[end]
            # if list1[entry] has all its characters matched
            # add list1[entry] to the list of matches found
            # the longest match is the latest one to be added to the list
            for sindex in range(1, len(list1)):
                if lenlist1[sindex] == characterIndex:
                    found.append(list1[sindex])


# entry has been fully matched

# characterIndex now equal to list1_0_len which is a match
# or characterIndex is less than list1_0_len which is no match and
# return the longest match or null

    return found
    


def xlateMacroParam(characterGroup, macroArguments):
# characterGroup is matched against the parameter names given in the macro definition
# if characterGroup is a parameter name, the translation of the parameter is returned
# 
    found = 0
    # argEntry is an array of 3 elements
    argEntry = []
    #  print('entered xlateMacroParam')
    # argEntry[0] is a string
    # argEntry[1] is the translation
    # argEntry[2] is the default translation
    # if the string is found, return the translation
    # if no translation specified, return the default value
    # else return the string
    for entry in macroArguments:
        argEntry = entry
        if argEntry[0] == ',':                      # we do not translate commas
            continue
        if argEntry[0] == characterGroup:
            found = 1
            break
    if found:
         if  argEntry[1]:                                                      # return translation
              return argEntry[1]
         else:
              return argEntry[2]                                         # or the default translation
#         elif argEntry[2]:
#              return argEntry[2]
    else:
        return characterGroup




def xlateCharacters(inputLine):
    # test and translate character
    # build a mask of interesting characters
    # that could make up a macro name
    keyString = ""
    for idx in range(len(inputLine)):
        testCharacter = inputLine[idx]
        isMatched = txpatt.match(testCharacter)
        if isMatched:
            keyString = keyString + testCharacter
        else:
            keyString = keyString + " "

    return keyString


def processInputLine(inputLine):
    # move with translation
    # copy and replace
    # scan for first macro name, else copy chars to output
#    global macroNameStack
# used to prevent recursive macro calls
    global processComplete
    macroNameStack = []
    macroCallDepth = 0       #  depth of macro calls
    outputString = ""
    idx = 0
    savedInputLine = inputLine
    keyString = xlateCharacters(inputLine)

    while idx < len(keyString):
        # while some inputLine
        #    copy masked uninteresting characters
        while (idx < len(keyString)) and (keyString[idx] == " "):
            w_char = inputLine[idx]
            outputString = outputString + w_char
            idx += 1
        svidx = idx
        #    svidx points to start of text
        characterGroup = ""
        #         start of interesting characters
        while (idx < len(keyString)) and (keyString[idx] != " "):
            characterGroup = characterGroup + keyString[idx]
            idx += 1


#  consume characterGroup
        while len(characterGroup) > 0:
            #                 testtoken is a list
            processComplete = False
            testtoken = ismacro(characterGroup)   # testtoken is a list, either null, or a macro in list form
            # macro name will be (leading) chars of characterGroup
            if testtoken:
                 inputLine = processMacro(testtoken, inputLine, svidx)
#                 print('1',inputLine)         #debug fixme
                 if processComplete:                      # found valid macro expansion which is prepended to input line
                      macroCallDepth += 1
                      if macroCallDepth > 40:  # presumed recursive macro call
                            print(msgHeader, 'recursive macro call')
                            print(msgHeader, savedInputLine,'\n')
                            print(macroNameStack) 
                            leading = characterGroup[:1]
                            outputString = outputString + leading        # output leading character
#                            print(outputString)
                            svidx += 1
                            if len(characterGroup) > 1:
                               characterGroup = characterGroup[1:]     # reduce input line by one character
                      else:
                            macroNameStack.append(testtoken[0])      # add macro name to list of expanded macros
                            characterGroup = ""  # to stop loop    # for next iteration
                            keyString = xlateCharacters(inputLine)
                            idx = 0
                 else:                                                                             # invalid macro call, same action as if not a macro
                      leading = characterGroup[:1]
                      outputString = outputString + leading        # output leading character
                      svidx += 1
                      if len(characterGroup) > 1:
                          characterGroup = characterGroup[1:]     # reduce input line by one character
                      else:
                          characterGroup = ""
            else:
                # has not touched inputLine
                # strip off leading char of characterGroup and output
                # try to match macro name with remainder of string characterGroup
                # till macro name found
                # or characterGroup consumed and sent to output
                leading = characterGroup[:1]
                outputString = outputString + leading
                svidx += 1
                if len(characterGroup) > 1:
                    characterGroup = characterGroup[1:]
                else:
                    characterGroup = ""
    return outputString


def processMacroBody(macroBody, macroArguments):
    # move with translation
    # copy and replace
    # expand macro parameters in macro body
    # scan for first param name, else copy to output
    outputString = ""
    idx = 0
    keyString = xlateCharacters(macroBody)

    while idx < len(keyString):
        # while some macroBody
        #    copy masked uninteresting characters
        while (idx < len(keyString)) and (keyString[idx] == " "):
            w_char = macroBody[idx]
            outputString = outputString + w_char
            idx += 1
        svidx = idx
        #    svidx points to start of text
        characterGroup = ""
        #         start of interesting characters
        while (idx < len(keyString)) and (keyString[idx] != " "):
            characterGroup = characterGroup + keyString[idx]
            idx += 1


#  consume characterGroup

        while len(characterGroup) > 0:
            #                 testtoken is a list
            testtoken = isMacroParameter(characterGroup, macroArguments)
            # parameter name will be (leading) chars of characterGroup
            if testtoken:
                characterGroup = ""  # to stop loop        ## A
                macroBody = macroBody[svidx:]
                pname = testtoken[-1]
                macroBody = chomp(pname, macroBody)

                ## point to the beginning of the parameter name

                # substitute translation for parameter name
                translated = xlateMacroParam(pname, macroArguments)
                if translated:
                    # remove macro parameter name from processing line

                    outputString = outputString + translated
                keyString = xlateCharacters(macroBody)  ## B
                idx = 0
            else:
                # has not touched macroBody
                # strip off leading char of characterGroup and output to outputString
                # try to match parameter name with remainder of string mbody
                # till parameter name found
                # or characterGroup consumed and sent to output
                leading = characterGroup[:1]
                outputString = outputString + leading
                svidx += 1
                if len(characterGroup) > 1:
                    characterGroup = characterGroup[1:]
                else:
                    characterGroup = ""
    return outputString


def chomp(s1, s2):
    #subtract string 1 from string 2
    if len(s1) > len(s2):
        return ""


# string 1 longer than string 2

    idx = 0
    while idx < len(s1):
        if s1[idx] != s2[idx]:
            break
        idx += 1
    s3 = ""
    while idx < len(s2):
        s3 = s3 + s2[idx]
        idx += 1
    return s3
    
def processMacro(currentMacro, inputLine, svidx):
    ## inputLine is the input line to be parsed
    ## reduce inputLine
    ## take off the macro name
    ## then prepend macro expansion to inputLine
    ## return inputLine
    ##  print(inputLine)      #debug
    global processComplete
    processComplete = False
    inputLine_save = inputLine
    inputLine = inputLine[svidx:]
    workMacro = {
            'mname': '',
            'margs': '',
            'mbody': ''
            }

    if currentMacro:
        if len(currentMacro) > 0:
            workMacro['mname'] = currentMacro[0]
        else:
            return inputLine        
        if len(currentMacro) > 1:
            workMacro['margs'] = currentMacro[1]    
        if len(currentMacro) > 2:
            workMacro['mbody'] = currentMacro[2]    
    else:
        return inputLine  
    ## point to the beginning of the macro
    if currentMacro[0]:
        inputLine = chomp(currentMacro[0], inputLine)
# if macro name in db, remove macro name from processing line
    peek = ""
    # test for macro with parameters
    if len(currentMacro[1]) > 0:
        if len(inputLine) > 0:
            # if some inputLine
            peek = inputLine[0]
            # look for ( to mark arguments to follow
            if peek != '(':
#                print(msgHeader,'macro ', currentMacro[0], ' missing arguments')
#                print(msgHeader,'at ', inputLine_save)
                processComplete = False
                return  inputLine_save
        else:
            # no more input
#            print(msgHeader,'macro ', currentMacro[0], ' missing arguments')
#            print(msgHeader,'at ', inputLine_save)
            processComplete = False
            return  inputLine_save
# 
    else:
        # no parameters
        inputLine = currentMacro[2] + inputLine
        processComplete = True
        return inputLine
# simple macro expansion replaces macro name

# we have macro defined with parameters
# now process user input
# remove leading parenthesis
    inputLine = chomp(peek, inputLine)
    userGivenMacroArgs = ""
    bracketDepth = 1
    idx = 0
    while (idx < len(inputLine)) and (bracketDepth != 0):
        tok = inputLine[idx]
        if tok == '(':
            bracketDepth += 1
        if tok == ')':
            bracketDepth += -1
        userGivenMacroArgs = userGivenMacroArgs + tok
        idx += 1
    if bracketDepth != 0:
        print(msgHeader,'get macro parameters on input line')
        print(msgHeader,'imbalanced brackets')
        print(msgHeader,inputLine)
        processComplete = False
        return inputLine_save
# fix to prevent loops                                 fixme

# remove arguments from input line
    inputLine = chomp(userGivenMacroArgs, inputLine)
    # drop closing parenthesis
    userGivenMacroArgs = userGivenMacroArgs[:-1]
    # print('userGivenMacroArgs ', userGivenMacroArgs)                  #debug
    # userGivenMacroArgs has our calling arguments
    # parse userGivenMacroArgs into positional parameters
    # into a list of strings
    idx = 0
    paramString = ""  # our work string
    # to accumulate substrings
    # each argument is a substring
    userGivenMacroArgList = []  # list of paramStrings
    while idx < len(userGivenMacroArgs):
        tok = userGivenMacroArgs[idx]
        if tok == '(':
            bracketDepth = 1  # we have nested brackets in call
            paramString = paramString + tok
            idx += 1
            while idx < len(userGivenMacroArgs) and (bracketDepth != 0):
                tok = userGivenMacroArgs[idx]
                if tok == '(':
                    bracketDepth += 1
                if tok == ')':
                    bracketDepth += -1
                paramString = paramString + tok
                idx += 1
            if bracketDepth != 0:
                print(msgHeader,'get macro parameters on input line')
                print(msgHeader,'imbalanced brackets')
                print(msgHeader,inputLine)
                processComplete = False
                return inputLine_save
        # have we exhausted input?
            if idx >= len(userGivenMacroArgs):
                userGivenMacroArgList.append(paramString.strip())
                paramString = ""
                continue
        # we still have input chars to process
        # did we end on a comma?              # boundary conditions
            if userGivenMacroArgs[idx] == ',':
                userGivenMacroArgList.append(paramString.strip())
                paramString = ""
                userGivenMacroArgList.append(',')
                idx += 1
                continue
        if isquote(tok):
            quotedString = tok
            idx += 1
            while (idx < len(userGivenMacroArgs)) and (userGivenMacroArgs[idx]
                                                       != tok):
                quotedString = quotedString + userGivenMacroArgs[idx]
                idx += 1
            if idx < len(userGivenMacroArgs):
                quotedString = quotedString + userGivenMacroArgs[idx]  # trailing quote
                paramString = paramString + quotedString
                quotedString = ""
                idx += 1
                # did we end on a comma?              # boundary conditions
                if idx < len(userGivenMacroArgs):
                    if userGivenMacroArgs[idx] == ',':
                        userGivenMacroArgList.append(paramString)
                        paramString = ""
                        userGivenMacroArgList.append(',')
                        idx += 1
                        continue

            else:
                print(msgHeader,'unbalanced quotes on input line')
                print(msgHeader,inputLine)
                processComplete = False
                return inputLine_save
            if idx >= len(userGivenMacroArgs):
                userGivenMacroArgList.append(paramString)
                paramString = ""
                continue
    # ordinary character
        if tok == ',':
            userGivenMacroArgList.append(paramString)
            userGivenMacroArgList.append(',')
            paramString = ""
            idx += 1
            continue
        paramString = paramString + userGivenMacroArgs[idx]
        idx += 1
        if idx >= len(userGivenMacroArgs):
            userGivenMacroArgList.append(paramString)
            paramString = ""

# we have a comma-separated list of arguments in userGivenMacroArgList
# commas are significant
    macroDefinedArgs = workMacro['margs'][1:-1]
    #  drop enclosing brackets
    mlist = []  # parse macro parameters given in macro definition  to macro parameter list
    defaultList = []   # for default parameter values
    pstring = ""
    idx = 0
    while idx < len(macroDefinedArgs):            # building a list of args given in macro definition
        tok = macroDefinedArgs[idx]
        if ( tok != ',') and ( tok != '='):
            pstring = pstring + tok
        else:                                                                    # end of current token
            mlist.append(pstring.strip())         # we are needlessly adding a trailing comma - fixme
            pstring = ""
            mlist.append(',')
            if tok != '=':
                defaultList.append('')
                defaultList.append(',')
            else: # we have a default value
                 defaultString = ""
                 delimStack = []
                 quotedString = ''
                 svQuote = ''
                 idx += 1
                 while idx < len(macroDefinedArgs):
                     tok = macroDefinedArgs[idx]
                     if (tok == ',') and (len(delimStack) < 1):
                        break     # end of default parameter
                     if isquote(tok):
                         quotedString = tok
                         svQuote = tok
                         idx += 1
                         while (idx < len(macroDefinedArgs)) and (macroDefinedArgs[idx]
                                                       != svQuote):
                               quotedString = quotedString + macroDefinedArgs[idx]
                               idx += 1
                         if idx < len(macroDefinedArgs):
                              quotedString = quotedString + macroDefinedArgs[idx]  # trailing quote
                         defaultString = defaultString + quotedString
                     elif tok == ')' or tok == ']' or tok == '\}':
                         if delimStack[-1] == tok:
                             del delimStack[-1]
                         else:
                             print(msgHeader, 'delimeter stack out of sync')
                             print(msgHeader, 'token ', tok, ' stack ', delimStack)
                     elif tok =='(' or tok == '[' or tok == '\{':
                             delimStack.append(matchDelim(tok))
                     defaultString = defaultString + tok
                     idx += 1  
                 defaultList.append(defaultString)
                 defaultList.append(',')
        idx += 1
    if pstring:                                                             # for trailing argument, if any
        mlist.append(pstring.strip())
        defaultList.append('')
    if len(mlist) != len(defaultList):
         print(msgHeader, "mlist, defaultList mismatch ", str(len(mlist)), " ", str(len(defaultList)))

# test userGivenMacroArgList for trailing , and delete
#    print(userGivenMacroArgList)
    if userGivenMacroArgList:
        if userGivenMacroArgList[-1] == ',':
             tok = userGivenMacroArgList.pop(-1)       # discard tok
# set up a list of corresponding pairs of macro parameters
    macroArguments = []
    idx = 0
    while idx < len(mlist):
        m1 = mlist[idx]                                                  # m1 is placeholder parameter in the macro definition
        m3 = defaultList[idx]                                    # m3 is default for this parameter
        if idx < len(userGivenMacroArgList):
            m2 = userGivenMacroArgList[idx]    # m2 is user-given parameter in the macro call
        else:
            m2 = ""
        macroArguments.append([m1, m2, m3])  # third entry is for default args
        # build list of lists
        idx += 1
    if idx < len(userGivenMacroArgList):
        print(msgHeader,'macro ', currentMacro[0], ' too many calling parameters')
        print(msgHeader,'expected ', mlist)
        print(msgHeader,'found    ', userGivenMacroArgList)
        processComplete = False
        return inputLine_save

    x_l = workMacro['mbody']
    xpandedBody = processMacroBody(x_l, macroArguments)
    inputLine = xpandedBody + inputLine
    processComplete = True
    return inputLine                    # valid macro call is expanded and prepended to input line


def ismacro(characterGroup):
    global macrodb
    mname = characterGroup
    searchlist = [characterGroup]

    currentMacro = []
    mkeys = macrodb.keys()  # list the keys to macrodb

    for entry in mkeys:
        if macrodb[entry] == 'mname':  # if it is a macro name
            searchlist.append(entry)


#   collect macro names and add them to searchlist

    found = trieSearch(searchlist)  # match longest string
    if not found:
        return []  # not a macro name - return null

    mname = found[-1]
    mname_args = mname + '_args'
    mname_body = mname + '_body'
    try:
        currentMacro.append(mname)
        currentMacro.append(macrodb[mname_args])
        currentMacro.append(macrodb[mname_body])
    except:
        print(msgHeader,'macro ', characterGroup, ' invalid expansion in db')
        currentMacro = []

    return currentMacro


def isMacroParameter(characterGroup, macroArguments):
# search in the macro body for a parameter name from the macro definition
# macroArguments is an array composed of entries of three elements each
# parameter name defined in macro definition
# user substitution for that name or characters
# default value for that name, if no user value given
    searchlist = [characterGroup]
    found = []
    for idx in range(0, len(macroArguments)):
        if macroArguments[idx][0] != ',':
            searchlist.append(macroArguments[idx][0])
    found = trieSearch(searchlist)
    return found


# return the longest match or null list
 

def buildMacro(mname,mbody):
    global macrodb
    margs = ''
    mname = mname.strip()
    if not mbody:
        margskey = mname + '_args'
        mbodykey = mname + '_body'
        macrodb[mname] = 'deleted'
        macrodb[margskey] = ''
        macrodb[mbodykey] = ''
        return
    if mbody[:1] == '(':
        margs = '('
        bracketDepth = 1
        idx = 1
        while (idx < len(mbody)) and (bracketDepth != 0):
            tok = mbody[idx]
            if tok == '(':
                bracketDepth += 1
            if tok == ')':
                bracketDepth += -1
            margs = margs + tok
            idx += 1
        if bracketDepth != 0:
            print(msgHeader,'get macro parameters on input line')
            print(msgHeader,'imbalanced brackets')
            print(msgHeader,mname, mbody)
            return
# remove arguments from input line
        mbody  = chomp(margs, mbody)
    mbody = mbody.rstrip()
    if margs:
        if not mbody:
           mbody = margs
           margs = ''
    margskey = mname + '_args'
    mbodykey = mname + '_body'
    macrodb[mname] = 'mname'
    macrodb[margskey] = margs
    macrodb[mbodykey] = mbody
#    print('1',mname)                                     # debug macro   fixme
#    print('2',margs)
#    print('3',mbody)
    return


def main():
    global ipfstack
    global fnamestack
    global eofind
    if len(sys.argv) > 1:
      input_file_name = sys.argv[1]
    else:
      print(msgHeader,'usage: program input_file_name')
      exit(0)
    if not getfile(input_file_name):
        print(msgHeader,'cannot access first file given')
        exit(0)   
# we have the first file put to ipfstack and filename stack
    while len(ipfstack) > 0:

        while not eofind:
            p_l = get_line(ipfstack[-1])
            if not p_l:
                continue           # null line means end of file
            matchobj = pattInclude.match(p_l)
            if matchobj:
                start,stop = matchobj.span(1)
                filename = p_l[start:stop]
#                   print('include ', filename)
                if getfile(filename):             # access included file
                    continue
            matchobj = pattDefine.match(p_l)
            if matchobj:
                mname = matchobj.group(1)
                mbody   = matchobj.group(2)
                buildMacro(mname,mbody)
                continue
            sys.stdout.write(processInputLine(p_l))  # we do not want a newline character to be appended
            
        ipfstack[-1].close()
        if len(ipfstack) > 0:
            ipf = ipfstack.pop(-1)                                      # is discarded
            fn =   fnamestack.pop(-1)                             # is discarded
            eofind = False
    return

if __name__=='__main__':
    main()




