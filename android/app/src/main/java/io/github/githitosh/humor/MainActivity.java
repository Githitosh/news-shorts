package io.github.githitosh.humor;

import android.app.Activity;
import android.content.ContentValues;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.Map;

/**
 * The Humor page in an app. The page and its music are inside the app (assets) and are served
 * from https://appassets.androidplatform.net/assets/, so the page works as it does on the web:
 * it reads X, the news and the translations over the internet, and keeps its settings.
 * Links to other sites open in the browser. Download saves the MP4 to Movies/Humor.
 */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final String START = "https://" + HOST + "/assets/humor/index.html";
    private static final String SITE = "https://githitosh.github.io/news-shorts/";

    private FrameLayout root;
    private WebView web;
    private View fullView;
    private WebChromeClient.CustomViewCallback fullDone;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        root = new FrameLayout(this);
        web = new WebView(this);
        root.addView(web, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setTextZoom(100);
        web.addJavascriptInterface(new Bridge(), "AndroidApp");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                String path = u.getPath();
                if (HOST.equals(u.getHost()) && path != null && path.startsWith("/assets/")) return asset(path.substring("/assets/".length()));
                return null;
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                String path = u.getPath() == null ? "" : u.getPath();
                if (HOST.equals(u.getHost())) {
                    if (path.startsWith("/assets/humor")) return false;
                    /* The News link: the News page on the web. */
                    open(Uri.parse(SITE + path.replaceFirst("^/assets/?", "")));
                    return true;
                }
                open(u);
                return true;
            }
        });

        /* Full screen: the page asks for it, and the app shows that picture over everything. */
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onShowCustomView(View view, CustomViewCallback done) {
                if (fullView != null) { done.onCustomViewHidden(); return; }
                fullView = view;
                fullDone = done;
                root.addView(view, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
                web.setVisibility(View.INVISIBLE);
                immersive(true);
            }

            @Override
            public void onHideCustomView() {
                leaveFull();
            }
        });

        if (state != null) web.restoreState(state);
        else web.loadUrl(START);
    }

    private void leaveFull() {
        if (fullView == null) return;
        root.removeView(fullView);
        fullView = null;
        web.setVisibility(View.VISIBLE);
        immersive(false);
        if (fullDone != null) fullDone.onCustomViewHidden();
        fullDone = null;
    }

    @SuppressWarnings("deprecation")
    private void immersive(boolean on) {
        View d = getWindow().getDecorView();
        d.setSystemUiVisibility(on
                ? View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                  | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                : View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
    }

    private void open(Uri u) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, u));
        } catch (Exception e) {
            Toast.makeText(this, u.toString(), Toast.LENGTH_SHORT).show();
        }
    }

    private WebResourceResponse asset(String path) {
        if (path.isEmpty() || path.endsWith("/")) path += "index.html";
        String mime = path.endsWith(".html") ? "text/html"
                : path.endsWith(".m4a") ? "audio/mp4"
                : path.endsWith(".png") ? "image/png"
                : path.endsWith(".js") ? "text/javascript"
                : path.endsWith(".json") ? "application/json"
                : "application/octet-stream";
        try {
            InputStream in = getAssets().open(path);
            WebResourceResponse res = new WebResourceResponse(mime, mime.startsWith("text/") || mime.endsWith("json") ? "utf-8" : null, in);
            Map<String, String> headers = new HashMap<>();
            headers.put("Cache-Control", "no-cache");
            res.setResponseHeaders(headers);
            return res;
        } catch (IOException e) {
            return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", new HashMap<>(), new ByteArrayInputStream(new byte[0]));
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (fullView != null) {
            web.evaluateJavascript("document.exitFullscreen && document.exitFullscreen()", null);
            leaveFull();
            return;
        }
        /* Back closes Settings first; on the video it leaves the app. */
        web.evaluateJavascript(
                "(function(){var s=document.getElementById('studio');if(s&&!s.hidden){document.getElementById('backVideo').click();return 1;}return 0;})()",
                v -> {
                    if (!"1".equals(v)) {
                        if (web.canGoBack()) web.goBack();
                        else finish();
                    }
                });
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    protected void onDestroy() {
        root.removeAllViews();
        web.destroy();
        super.onDestroy();
    }

    /** Download: the page sends the MP4 in pieces; it is written to Movies/Humor. */
    private class Bridge {
        private OutputStream out;
        private Uri uri;
        private String where = "";

        @JavascriptInterface
        public boolean saveStart(String name, String mime) {
            close();
            try {
                if (Build.VERSION.SDK_INT >= 29) {
                    ContentValues v = new ContentValues();
                    v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
                    v.put(MediaStore.MediaColumns.MIME_TYPE, mime);
                    v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_MOVIES + "/Humor");
                    v.put(MediaStore.MediaColumns.IS_PENDING, 1);
                    uri = getContentResolver().insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, v);
                    if (uri == null) return false;
                    out = getContentResolver().openOutputStream(uri);
                    where = "Movies/Humor";
                } else {
                    /* Android 8 and 9: the app's own Movies folder, which needs no permission. */
                    File dir = getExternalFilesDir(Environment.DIRECTORY_MOVIES);
                    if (dir == null) return false;
                    dir.mkdirs();
                    File f = new File(dir, name);
                    out = new FileOutputStream(f);
                    uri = null;
                    where = f.getAbsolutePath();
                }
                return out != null;
            } catch (Exception e) {
                close();
                return false;
            }
        }

        @JavascriptInterface
        public boolean saveChunk(String base64) {
            if (out == null) return false;
            try {
                out.write(Base64.decode(base64, Base64.DEFAULT));
                return true;
            } catch (Exception e) {
                return false;
            }
        }

        @JavascriptInterface
        public String saveEnd() {
            if (out == null) return "";
            try {
                out.close();
                out = null;
                if (uri != null && Build.VERSION.SDK_INT >= 29) {
                    ContentValues v = new ContentValues();
                    v.put(MediaStore.MediaColumns.IS_PENDING, 0);
                    getContentResolver().update(uri, v, null, null);
                }
                final String shown = where;
                runOnUiThread(() -> Toast.makeText(MainActivity.this, getString(R.string.saved, shown), Toast.LENGTH_LONG).show());
                return where;
            } catch (Exception e) {
                close();
                return "";
            }
        }

        private void close() {
            if (out != null) {
                try { out.close(); } catch (IOException ignored) { }
            }
            out = null;
        }
    }
}
