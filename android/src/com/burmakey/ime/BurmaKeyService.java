package com.burmakey.ime;

import android.inputmethodservice.InputMethodService;
import android.view.View;
import android.view.Gravity;
import android.view.inputmethod.InputConnection;
import android.widget.Button;
import android.widget.LinearLayout;
import android.graphics.Color;

/**
 * BurmaKey — walking-skeleton IME.
 *
 * This first slice proves the plumbing only: it registers as a system
 * keyboard, draws a Latin key grid built in code (no layout XML), and commits
 * the tapped letters into whatever text field is focused. The v4 engine and
 * the suggestion bar come next; this milestone is "does a real Android app
 * accept our keyboard and let it type into another app's text box."
 */
public class BurmaKeyService extends InputMethodService {

    private static final String[] ROWS = {
        "qwertyuiop", "asdfghjkl", "zxcvbnm"
    };

    @Override
    public View onCreateInputView() {
        LinearLayout kb = new LinearLayout(this);
        kb.setOrientation(LinearLayout.VERTICAL);
        kb.setBackgroundColor(Color.parseColor("#0b141a"));
        kb.setPadding(6, 8, 6, 14);

        for (String row : ROWS) kb.addView(letterRow(row));
        kb.addView(bottomRow());
        return kb;
    }

    private LinearLayout letterRow(String letters) {
        LinearLayout row = newRow();
        for (int i = 0; i < letters.length(); i++) {
            final String ch = String.valueOf(letters.charAt(i));
            row.addView(key(ch, 1f, () -> commit(ch)));
        }
        return row;
    }

    private LinearLayout bottomRow() {
        LinearLayout row = newRow();
        row.addView(key("⌫", 1.5f, this::backspace));   // ⌫
        row.addView(key("space", 4f, () -> commit(" ")));
        row.addView(key("↵", 1.5f, this::enter));       // ↵
        return row;
    }

    private LinearLayout newRow() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT);
        row.setLayoutParams(lp);
        return row;
    }

    private Button key(String label, float weight, Runnable action) {
        Button b = new Button(this);
        b.setText(label);
        b.setAllCaps(false);
        b.setTextColor(Color.parseColor("#e9edef"));
        b.setBackgroundColor(Color.parseColor("#2a3942"));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            0, LinearLayout.LayoutParams.WRAP_CONTENT, weight);
        lp.setMargins(3, 3, 3, 3);
        b.setLayoutParams(lp);
        b.setOnClickListener(v -> action.run());
        return b;
    }

    private void commit(String s) {
        InputConnection ic = getCurrentInputConnection();
        if (ic != null) ic.commitText(s, 1);
    }

    private void backspace() {
        InputConnection ic = getCurrentInputConnection();
        if (ic != null) ic.deleteSurroundingText(1, 0);
    }

    private void enter() {
        commit("\n");
    }
}
