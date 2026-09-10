package com.burmakey.ime;

import android.inputmethodservice.InputMethodService;
import android.view.View;
import android.view.inputmethod.InputConnection;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.graphics.Color;
import android.util.TypedValue;
import java.util.List;

/**
 * BurmaKey IME with the v4 engine wired in.
 *
 * Type Burglish; the candidate bar shows Burmese words; tap one (or press
 * space) to commit real Unicode into the focused field. This is the web
 * keyboard's core loop, on Android.
 */
public class BurmaKeyService extends InputMethodService {

    private static final String[] ROWS = {"qwertyuiop", "asdfghjkl", "zxcvbnm"};
    private final Engine engine = new Engine();
    private final StringBuilder buf = new StringBuilder();   // Burglish being typed
    private LinearLayout bar;                                 // candidate strip
    private List<Integer> cands;

    @Override
    public void onCreate() {
        super.onCreate();
        try { engine.load(getAssets().open("weblex_v4.txt")); } catch (Exception e) { /* keys still work */ }
    }

    @Override
    public View onCreateInputView() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#0b141a"));
        root.setPadding(6, 6, 6, 14);

        HorizontalScrollView sv = new HorizontalScrollView(this);
        sv.setHorizontalScrollBarEnabled(false);
        bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setMinimumHeight(dp(52));
        sv.addView(bar);
        root.addView(sv);

        for (String row : ROWS) root.addView(letterRow(row));
        root.addView(bottomRow());
        drawBar();
        return root;
    }

    // ---- key rows -------------------------------------------------------
    private LinearLayout letterRow(String letters) {
        LinearLayout row = newRow();
        for (int i = 0; i < letters.length(); i++) {
            final char ch = letters.charAt(i);
            row.addView(key(String.valueOf(ch), 1f, () -> onLetter(ch)));
        }
        return row;
    }
    private LinearLayout bottomRow() {
        LinearLayout row = newRow();
        row.addView(key("⌫", 1.5f, this::onBackspace));
        row.addView(key("space", 4f, this::onSpace));
        row.addView(key("↵", 1.5f, this::onEnter));
        return row;
    }
    private LinearLayout newRow() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        return row;
    }
    private Button key(String label, float weight, Runnable action) {
        Button b = new Button(this);
        b.setText(label); b.setAllCaps(false);
        b.setTextColor(Color.parseColor("#e9edef"));
        b.setBackgroundColor(Color.parseColor("#2a3942"));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT, weight);
        lp.setMargins(3, 3, 3, 3);
        b.setLayoutParams(lp);
        b.setOnClickListener(v -> action.run());
        return b;
    }

    // ---- candidate bar --------------------------------------------------
    private void drawBar() {
        if (bar == null) return;
        bar.removeAllViews();
        if (buf.length() == 0) return;
        cands = engine.size() > 0 ? engine.candidates(buf.toString().toLowerCase()) : null;
        if (cands != null)
            for (final int id : cands) bar.addView(candidate(engine.word(id), engine.spelling(id),
                                                             () -> pickWord(id)));
        // an always-available "as typed" chip
        bar.addView(candidate(buf.toString(), "as typed", this::pickRaw));
    }
    private View candidate(String big, String small, Runnable action) {
        LinearLayout cell = new LinearLayout(this);
        cell.setOrientation(LinearLayout.VERTICAL);
        cell.setBackgroundColor(Color.parseColor("#17232b"));
        cell.setPadding(dp(14), dp(6), dp(14), dp(6));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(4, 2, 4, 2); cell.setLayoutParams(lp);
        cell.setMinimumWidth(dp(56));
        TextView t = new TextView(this);
        t.setText(big); t.setTextColor(Color.parseColor("#e9edef"));
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 19);
        TextView s = new TextView(this);
        s.setText(small); s.setTextColor(Color.parseColor("#8696a0"));
        s.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
        cell.addView(t); cell.addView(s);
        cell.setOnClickListener(v -> action.run());
        return cell;
    }

    // ---- input handling -------------------------------------------------
    private void onLetter(char ch) { buf.append(ch); drawBar(); }

    private void onBackspace() {
        if (buf.length() > 0) { buf.deleteCharAt(buf.length() - 1); drawBar(); return; }
        InputConnection ic = getCurrentInputConnection();
        if (ic != null) ic.deleteSurroundingText(1, 0);
    }
    private void onSpace() {
        if (buf.length() > 0 && cands != null && !cands.isEmpty()) { pickWord(cands.get(0)); return; }
        if (buf.length() > 0) { pickRaw(); return; }
        commit(" "); engine.endMessage();
    }
    private void onEnter() {
        if (buf.length() > 0) { if (cands != null && !cands.isEmpty()) pickWord(cands.get(0)); else pickRaw(); }
        commit("\n"); engine.endMessage();
    }
    private void pickWord(int id) {
        String w = engine.word(id);
        commit(w); engine.learn(w);
        buf.setLength(0); drawBar();
    }
    private void pickRaw() {
        commit(buf.toString()); engine.endMessage();
        buf.setLength(0); drawBar();
    }
    private void commit(String s) {
        InputConnection ic = getCurrentInputConnection();
        if (ic != null) ic.commitText(s, 1);
    }

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density + 0.5f);
    }
}
