package com.woozypictures.frostedglass;

import android.app.Activity;
import android.app.Dialog;
import android.content.Intent;
import android.graphics.Paint;
import android.net.Uri;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.ColorDrawable;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.view.inputmethod.EditorInfo;
import android.widget.AdapterView;
import android.widget.BaseAdapter;
import android.widget.EditText;
import android.widget.GridView;
import android.widget.ImageView;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import java.util.ArrayList;
import java.util.Locale;

public class MainActivity extends Activity {

    static final String[] LABELS = {/*LABELS*/};
    static final String[] DRAWABLES = {/*DRAWABLES*/};
    static final String[] PACKAGES = {/*PACKAGES*/};
    static final String[] SOCIALS = {
        "https://www.instagram.com/woozypictures/",
        "https://www.youtube.com/@WoozyPictures",
        "https://x.com/WoozyPictures",
    };

    final ArrayList<Integer> shown = new ArrayList<Integer>();
    IconAdapter adapter;
    TextView countView;

    int dp(float v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, getResources().getDisplayMetrics());
    }

    GradientDrawable glass(float radiusDp, int fillAlpha) {
        GradientDrawable g = new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,
                new int[]{Color.argb(fillAlpha, 255, 255, 255), Color.argb(fillAlpha + 26, 255, 255, 255)});
        g.setCornerRadius(dp(radiusDp));
        g.setStroke(dp(1), Color.argb(90, 255, 255, 255));
        return g;
    }

    TextView text(String s, float sp, int alpha, boolean bold) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, sp);
        t.setTextColor(Color.argb(alpha, 255, 255, 255));
        t.setTypeface(Typeface.create("sans-serif", bold ? Typeface.BOLD : Typeface.NORMAL));
        return t;
    }

    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);
        Window w = getWindow();
        if (Build.VERSION.SDK_INT >= 21) {
            w.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
            w.setStatusBarColor(Color.TRANSPARENT);
            w.setNavigationBarColor(Color.TRANSPARENT);
            w.getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
            call(w, "setStatusBarContrastEnforced", false);
            call(w, "setNavigationBarContrastEnforced", false);
        }
        // one even tint over the whole screen, including behind the status and nav bars
        w.setBackgroundDrawable(new ColorDrawable(Color.argb(40, 0, 0, 0)));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(12), dp(20), dp(4));

        // Header card
        LinearLayout header = new LinearLayout(this);
        header.setOrientation(LinearLayout.VERTICAL);
        header.setBackground(glass(28, 46));
        header.setPadding(dp(22), dp(20), dp(22), dp(20));
        TextView title = text("FROSTED GLASS", 28, 255, true);
        title.setLetterSpacing(0.12f);
        header.addView(title);
        TextView by = text("BY MAHESH SHARMA", 12, 200, false);
        by.setLetterSpacing(0.14f);
        by.setPadding(0, dp(2), 0, 0);
        header.addView(by);
        countView = text(LABELS.length + " ICONS", 13, 190, false);
        countView.setLetterSpacing(0.1f);
        countView.setPadding(0, dp(4), 0, dp(12));
        header.addView(countView);
        TextView how = text("APPLY: Smart Launcher settings, Icon pack, Frosted Glass Icon Pack. Tap any icon to see it larger.", 13, 170, false);
        how.setLineSpacing(dp(2), 1f);
        header.addView(how);
        TextView about = text("ABOUT", 12, 230, true);
        about.setLetterSpacing(0.14f);
        about.setBackgroundColor(Color.TRANSPARENT);
        about.setPadding(0, dp(14), dp(24), dp(2));
        about.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) { showAbout(); }
        });
        header.addView(about, new LinearLayout.LayoutParams(-2, -2));
        root.addView(header, new LinearLayout.LayoutParams(-1, -2));

        // Search card
        EditText search = new EditText(this);
        search.setHint("SEARCH");
        search.setHintTextColor(Color.argb(150, 255, 255, 255));
        search.setTextColor(Color.WHITE);
        search.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        search.setLetterSpacing(0.06f);
        search.setSingleLine(true);
        search.setImeOptions(EditorInfo.IME_ACTION_DONE);
        search.setBackground(glass(24, 40));
        search.setPadding(dp(22), dp(14), dp(22), dp(14));
        LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(-1, -2);
        sp.topMargin = dp(12);
        sp.bottomMargin = dp(12);
        root.addView(search, sp);

        // Grid card
        GridView grid = new GridView(this);
        grid.setNumColumns(GridView.AUTO_FIT);
        grid.setColumnWidth(dp(80));
        grid.setStretchMode(GridView.STRETCH_COLUMN_WIDTH);
        grid.setVerticalSpacing(dp(6));
        grid.setClipToPadding(false);
        grid.setPadding(dp(8), dp(14), dp(8), dp(24));
        grid.setSelector(new ColorDrawable(Color.TRANSPARENT));
        grid.setVerticalScrollBarEnabled(false);
        grid.setBackground(glass(28, 30));
        LinearLayout.LayoutParams gp = new LinearLayout.LayoutParams(-1, 0, 1f);
        gp.bottomMargin = dp(12);
        root.addView(grid, gp);

        for (int i = 0; i < LABELS.length; i++) shown.add(i);
        adapter = new IconAdapter();
        grid.setAdapter(adapter);
        grid.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            public void onItemClick(AdapterView<?> p, View v, int pos, long id) {
                showIcon(shown.get(pos));
            }
        });

        search.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int a, int c, int d) {}
            public void onTextChanged(CharSequence s, int a, int c, int d) {}
            public void afterTextChanged(Editable e) {
                String q = e.toString().trim().toLowerCase(Locale.ROOT);
                shown.clear();
                for (int i = 0; i < LABELS.length; i++)
                    if (q.length() == 0 || LABELS[i].toLowerCase(Locale.ROOT).contains(q)) shown.add(i);
                countView.setText(q.length() == 0 ? LABELS.length + " ICONS" : shown.size() + " OF " + LABELS.length + " ICONS");
                adapter.notifyDataSetChanged();
            }
        });

        // outer frame absorbs the status/nav bar insets; inner padding stays intact
        FrameLayout frame = new FrameLayout(this);
        frame.setFitsSystemWindows(true);
        frame.addView(root, new FrameLayout.LayoutParams(-1, -1));
        setContentView(frame);
    }

    static void call(Object target, String method, Object arg) {
        try {
            Class<?> t = arg instanceof Boolean ? boolean.class : int.class;
            target.getClass().getMethod(method, t).invoke(target, arg);
        } catch (Throwable ignored) { }
    }

    int iconRes(int i) {
        return getResources().getIdentifier(DRAWABLES[i], "drawable", getPackageName());
    }

    void showIcon(int i) {
        Dialog d = new Dialog(this);
        d.requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER_HORIZONTAL);
        box.setPadding(dp(28), dp(28), dp(28), dp(24));
        GradientDrawable card = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{Color.argb(235, 58, 62, 72), Color.argb(235, 30, 32, 38)});
        card.setCornerRadius(dp(32));
        card.setStroke(dp(1), Color.argb(80, 255, 255, 255));
        box.setBackground(card);
        ImageView big = new ImageView(this);
        big.setImageResource(iconRes(i));
        box.addView(big, new LinearLayout.LayoutParams(dp(150), dp(150)));
        TextView name = text(LABELS[i].toUpperCase(Locale.ROOT), 20, 255, true);
        name.setLetterSpacing(0.08f);
        name.setGravity(Gravity.CENTER);
        name.setPadding(0, dp(16), 0, dp(4));
        box.addView(name);
        TextView pkg = text(PACKAGES[i], 12, 170, false);
        pkg.setGravity(Gravity.CENTER);
        box.addView(pkg);
        d.setContentView(box);
        if (d.getWindow() != null) {
            d.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            d.getWindow().setLayout(dp(300), ViewGroup.LayoutParams.WRAP_CONTENT);
            d.getWindow().setDimAmount(0.6f);
            // blur the grid behind the popup on Android 12+
            WindowManager.LayoutParams lp = d.getWindow().getAttributes();
            if (Build.VERSION.SDK_INT >= 31) {
                d.getWindow().addFlags(0x4); // FLAG_BLUR_BEHIND
                call(lp, "setBlurBehindRadius", dp(24));
                d.getWindow().setAttributes(lp);
            }
        }
        d.show();
    }

    /** Created by Woozypictures, the version, and the socials (shared with HQ and HQ Fit). */
    void showAbout() {
        Dialog d = new Dialog(this);
        d.requestWindowFeature(Window.FEATURE_NO_TITLE);
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(28), dp(26), dp(28), dp(22));
        GradientDrawable card = new GradientDrawable(GradientDrawable.Orientation.TL_BR,
                new int[]{Color.argb(235, 58, 62, 72), Color.argb(235, 30, 32, 38)});
        card.setCornerRadius(dp(32));
        card.setStroke(dp(1), Color.argb(80, 255, 255, 255));
        box.setBackground(card);
        String version = "";
        try { version = getPackageManager().getPackageInfo(getPackageName(), 0).versionName; } catch (Exception ignored) { }
        TextView t1 = text("FROSTED GLASS", 20, 255, true);
        t1.setLetterSpacing(0.08f);
        box.addView(t1);
        TextView t2 = text("Created by Woozypictures", 15, 240, false);
        t2.setPadding(0, dp(10), 0, 0);
        box.addView(t2);
        TextView t3 = text("App version: " + version, 14, 190, false);
        t3.setPadding(0, dp(2), 0, dp(6));
        box.addView(t3);
        for (final String url : SOCIALS) {
            TextView link = text(url, 14, 255, false);
            link.setPaintFlags(link.getPaintFlags() | Paint.UNDERLINE_TEXT_FLAG);
            link.setPadding(0, dp(10), 0, dp(4));
            link.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception ignored) { }
                }
            });
            box.addView(link);
        }
        d.setContentView(box);
        if (d.getWindow() != null) {
            d.getWindow().setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
            d.getWindow().setLayout(dp(340), ViewGroup.LayoutParams.WRAP_CONTENT);
            d.getWindow().setDimAmount(0.6f);
        }
        d.show();
    }

    class IconAdapter extends BaseAdapter {
        public int getCount() { return shown.size(); }
        public Object getItem(int p) { return shown.get(p); }
        public long getItemId(int p) { return shown.get(p); }

        public View getView(int pos, View cv, ViewGroup parent) {
            LinearLayout cell;
            if (cv == null) {
                cell = new LinearLayout(MainActivity.this);
                cell.setOrientation(LinearLayout.VERTICAL);
                cell.setGravity(Gravity.CENTER_HORIZONTAL);
                cell.setPadding(0, dp(6), 0, dp(6));
                ImageView iv = new ImageView(MainActivity.this);
                cell.addView(iv, new LinearLayout.LayoutParams(dp(60), dp(60)));
                TextView tv = text("", 11, 230, false);
                tv.setGravity(Gravity.CENTER);
                tv.setSingleLine(true);
                tv.setEllipsize(android.text.TextUtils.TruncateAt.END);
                tv.setPadding(dp(2), dp(6), dp(2), 0);
                cell.addView(tv, new LinearLayout.LayoutParams(-1, -2));
            } else {
                cell = (LinearLayout) cv;
            }
            int i = shown.get(pos);
            ((ImageView) cell.getChildAt(0)).setImageResource(iconRes(i));
            ((TextView) cell.getChildAt(1)).setText(LABELS[i]);
            return cell;
        }
    }
}
