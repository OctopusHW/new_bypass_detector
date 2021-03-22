# new_bypass_detector

new_bypass_detector





# Running Example

### target example code from app-debug.apk

### run

type equal to 0 means default input (find the path of "Landroid/webkit/WebView; loadUrl (Ljava/lang/String;)V").

```
python3 new_bypass_detector.py {target.apk} {type}
```

```sh
$ python new_bypass_detector.py app-debug.apk 0
************START************
[*] Lcom/example/activity/WebViewActivity$1; shouldOverrideUrlLoading (Lcom/example/webview/DemoWebView; Ljava/lang/String;)Z
[*] Lcom/example/activity/WebViewActivity; url (Lcom/example/webview/DemoWebView; Ljava/lang/String;)V
[*] Lcom/example/webview/DemoWebView; loadUrl (Ljava/lang/String;)V
[*] Landroid/webkit/WebView; loadUrl (Ljava/lang/String;)V
*************END*************
************START************
[*] Lcom/example/JavaScriptInterface/DemoJavaScriptInterface; loadUrl (Ljava/lang/String;)V
[*] Lcom/example/webview/DemoWebView; loadUrl (Ljava/lang/String;)V
[*] Landroid/webkit/WebView; loadUrl (Ljava/lang/String;)V
*************END*************
```

type equal to 1 means custom input

```
python3 new_bypass_detector.py {target.apk} {type} {sink} {source}
```

```sh
$ python new_bypass_detector.py app-debug.apk 1 loadUrl shouldOverrideUrlLoading
Lcom/example/JavaScriptInterface/DemoJavaScriptInterface; loadUrl (Ljava/lang/String;)V
Lcom/example/webview/DemoWebView; loadUrl (Ljava/lang/String;)V
************START************
[*] Lcom/example/activity/WebViewActivity$1; shouldOverrideUrlLoading (Lcom/example/webview/DemoWebView; Ljava/lang/String;)Z
[*] Lcom/example/activity/WebViewActivity; url (Lcom/example/webview/DemoWebView; Ljava/lang/String;)V
[*] Lcom/example/webview/DemoWebView; loadUrl (Ljava/lang/String;)V
*************END*************
```

