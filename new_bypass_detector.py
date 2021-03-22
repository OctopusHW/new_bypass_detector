
import sys

from androguard.core.analysis.analysis import MethodClassAnalysis
from androguard.customize.hearandroguard import Heardroguard
from androguard.misc import AnalyzeAPK



class MethodClassAnalysisWrapper:
    #
    # @param method: Heardroguard
    # @param method: MethodClassAnalysis
    #

    def __init__(self, h, method):
        self.h = h
        self.method = method
        self.xrefto = set()
        self.xreffrom = set()
        if method:
            self.full_name = method.full_name

            for xrefto_tup in self.method.get_xref_to():
                classobj = xrefto_tup[0]
                methodobj = xrefto_tup[1]
                if not classobj.is_external():
                    self.xrefto.add(h._Heardroguard__dx.get_method_analysis(methodobj))

            for xreffrom_tup in self.method.get_xref_from():
                classobj = xreffrom_tup[0]
                methodobj = xreffrom_tup[1]
                if not classobj.is_external():
                    self.xreffrom.add(h._Heardroguard__dx.get_method_analysis(methodobj))
    #
    # @return : set(MethodClassAnalysisWrapper)
    #
    def get_xref_to(self):
        return self.xrefto
    #
    # @return : set(MethodClassAnalysisWrapper)
    #
    def get_xref_from(self):
        return self.xreffrom
    #
    # @return : set(MethodClassAnalysisWrapper)
    #
    def get_full_name(self):
        return self.full_name

# get objective function
# reurn {'smali_name': MethodClassAnalysisWrapper}
def find_function(h, descriptors):
    matched_functions = {}
    for method_name, method_analysis in h.get_methods().items():
        for descriptor in descriptors:
            if method_name.find(descriptor) >= 0:
                t_method=method_analysis.get_method()
                t_analysis=h._Heardroguard__dx.get_method_analysis(t_method)
                matched_functions[method_name] = MethodClassAnalysisWrapper(h, t_analysis)

    return matched_functions

# get JS func
# reurn {'smali_name': MethodClassAnalysisWrapper}
def get_javascript_interact(h):
    javascript_interacts = [
        # ("name", "Descriptor")
        " onConsoleMessage (Landroid/webkit/ConsoleMessage;)Z",
        " onJsAlert (Landroid/webkit/WebView; Ljava/lang/String; Ljava/lang/String; Landroid/webkit/JsResult;)Z",
        " onJsBeforeUnload (Landroid/webkit/WebView; Ljava/lang/String; Ljava/lang/String; Landroid/webkit/JsResult;)Z",
        " onJsConfirm (Landroid/webkit/WebView; Ljava/lang/String; Ljava/lang/String; Landroid/webkit/JsResult;)Z",
        " onJsPrompt (Landroid/webkit/WebView; Ljava/lang/String; Ljava/lang/String; Ljava/lang/String; Landroid/webkit/JsPromptResult;)Z",
        " onProgressChanged (Landroid/webkit/WebView; I)V",
        " onReceivedIcon (Landroid/webkit/WebView; Landroid/graphics/Bitmap;)V",
        " onReceivedTitle (Landroid/webkit/WebView; Ljava/lang/String;)V",
        " onShowFileChooser (Landroid/webkit/WebView; Landroid/webkit/ValueCallback; Landroid/webkit/WebChromeClient$FileChooserParams;)Z"
    ]

    return find_function(h, javascript_interacts)

# get interface
# reurn {'smali_name': MethodClassAnalysisWrapper}
def get_javascript_interface(h,interface):
    javascript_interfaces = interface

    return find_function(h, javascript_interfaces)

# get shouldOverrideUrlLoading
# reurn {'smali_name': MethodClassAnalysisWrapper}
def get_shouldoverride(h):
    shouldoverrides = [
        " shouldOverrideUrlLoading (Landroid/webkit/WebView; Ljava/lang/String;)Z",
        " shouldOverrideUrlLoading (Landroid/webkit/WebView; Landroid/webkit/WebResourceRequest;)Z",
        " shouldOverrideUrlLoading "
    ]

    return find_function(h, shouldoverrides)

# get loadUrl
# reurn {'smali_name': MethodClassAnalysisWrapper}
def get_loadUrl(h):
    loadUrl = [
        " loadUrl (Ljava/lang/String;)V"
    ]

    return find_function(h, loadUrl)

# get except
# reurn {'smali_name': MethodClassAnalysisWrapper}
def get_except(h):
    loadUrl = [
        "c (Ljava/lang/Class; Ljava/lang/String; [Ljava/lang/Class;)Ljava/lang/reflect/Method"
    ]

    return find_function(h, loadUrl)


#
# Find a call path from 'source_method' to 'sink_method'
# sink_method xref_to source_method
#
# @param sink_method : MethodClassAnalysisWrapper sink of path
# @param source_method : MethodClassAnalysisWrapper source of path
def find_path(h,sink_method, source_method, except_method=[]):

    stack = []  # stack for DFS [MethodClassAnalysisWrapper]
    path = [source_method.method]  # path to record   [MethodClassAnalysisWrapper]
    swept = [source_method] + except_method  # list to record function searched  [MethodClassAnalysisWrapper]

    paths = []  # All paths from target to func

    stageCount = {}  # trick for backtrace
    stage = 0

    # For each of the references
    refs = source_method.get_xref_to()
    stageCount[stage] = len(refs)
    for ref in refs:
        stack.append(ref)

    # Do DFS

    while (len(stack) > 0):
        upper_method = stack.pop()

        if isinstance(upper_method, tuple) == True:
            upme = h._Heardroguard__dx.get_method_analysis(upper_method[1])
        else:
            upme = upper_method

        if upme.full_name not in map(lambda x: (x.full_name if not isinstance(x, tuple) else x[1].full_name), path[-1].get_xref_to()):
            print("Wrong")
            return
            # path.pop()

        # append the Function in the Path
        path.append(upme)

        # record the Function searched
        swept.append(upme)

        # if we find the sink_method ,record it in the paths and trace back
        if (upme.full_name == sink_method):
            paths.append(list(path))

            matched = None
            for method in swept:
                if sink_method == method.full_name:
                    matched = method
                    break
            swept.remove(matched)

            path.pop()
            stageCount[stage] -= 1

            while (stageCount[stage] == 0 and stage > 0):
                del stageCount[stage]
                stage -= 1
                stageCount[stage] -= 1
                path.pop()

            continue
            print("FIND!!!")
            # break

        # For each of the references
        refs = upme.get_xref_to()

        # prevent from access searched Function again
        #refs = list(filter(lambda x: x.get_full_name() not in map(lambda x: x.get_full_name(), swept), refs))
        m = map(lambda x: (x.full_name if not isinstance(x, tuple) else x[1].full_name), swept)
        refs = list(filter(lambda x: (x.full_name if not isinstance(x, tuple) else x[1].full_name) not in m, refs))

        # push the Xref to the stack
        if len(refs) > 0:
            stage = stage + 1
            stageCount[stage] = len(refs)
            for method in refs:
                stack.append(method)
        # if current func do not has xref, backtrace the path
        else:
            dele = path.pop()
            stageCount[stage] -= 1

            while (stageCount[stage] == 0 and stage > 0):
                del stageCount[stage]
                stage -= 1
                stageCount[stage] -= 1
                path.pop()

    # print stageCount
    return paths

#
# print format
#
# @param sink_method : MethodClassAnalysisWrapper sink of path
# @param source_method : MethodClassAnalysisWrapper source of path
def printF(sink_method,source_method=[],except_method=[]):
    for sourceM in source_method:
        for path in find_path(hearlysis,sink_method,source_method[sourceM],except_method):
            print("************START************")
            for p in path:
                if isinstance(p, MethodClassAnalysisWrapper) or isinstance(p, MethodClassAnalysis) :
                    print("[*] " + str(p.full_name))
                #else:
                    #print(p)
            print("*************END*************")



if __name__ == '__main__':
    debug = False
    if len(sys.argv) < 2:
        print("Usage: ")
        print("      python3 new_bypass_detector.py {target.apk}")

    hearlysis = Heardroguard(*AnalyzeAPK(sys.argv[1]))

    #print("get_except")
    #exceptM = get_except(hearlysis)
    #print(exceptM)

    #print("get_loadUrl")
    #loadUrl = get_loadUrl(hearlysis)
    loadUrlStr = "Landroid/webkit/WebView; loadUrl (Ljava/lang/String;)V"

    print("get_shouldoverride")
    shouldoverride = get_shouldoverride(hearlysis)
    #print(shouldoverride)
    printF(loadUrlStr,shouldoverride,[])

    #print("get_javascript_interact")
    #interact=get_javascript_interact(hearlysis)
    #print(interact)
    #printF(loadUrl, interact, [])

    print("get_javascript_interface")
    interface = hearlysis.get_JavascriptInterface()#get_javascript_interface(hearlysis)
    interface = get_javascript_interface(hearlysis,interface)
    #print(interface)
    printF(loadUrlStr, interface, [])


#D:\code\new_bypass_detector\apk
