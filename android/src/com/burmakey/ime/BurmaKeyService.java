package com.burmakey.ime;

import android.inputmethodservice.InputMethodService;
import android.view.View;
import android.view.MotionEvent;
import android.view.HapticFeedbackConstants;
import android.view.KeyEvent;
import android.os.Handler;
import android.os.Looper;
import android.view.inputmethod.EditorInfo;
import android.text.InputType;
import android.view.inputmethod.InputConnection;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.graphics.Color;
import android.util.TypedValue;
import java.io.File;
import java.util.List;

public class BurmaKeyService extends InputMethodService {

    private final Engine engine = new Engine();
    private final StringBuilder buf = new StringBuilder();
    private LinearLayout root, bar, keyArea;
    private List<Engine.Cand> cands;
    private boolean shift = false;      // one-shot uppercase
    private boolean symbols = false;    // number/symbol page
    private boolean emoji = false;      // emoji page
    private boolean noLearn = false;    // password/OTP field: never learn
    private File stateFile;
    private final Handler repeatHandler = new Handler(Looper.getMainLooper());
    private Runnable repeatRunnable;

    private static final String[] LETTERS = {"qwertyuiop", "asdfghjkl", "zxcvbnm"};

    @Override
    public void onCreate() {
        super.onCreate();
        stateFile = new File(getFilesDir(), "learn.tsv");
        try { engine.load(getAssets().open("weblex_v4.txt")); } catch (Exception ignored) {}
        engine.loadState(stateFile);       // remember prior sessions
        try { engine.loadBigrams(getAssets().open("nextword.txt")); } catch (Exception ignored) {}
    }

    @Override
    public View onCreateInputView() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.parseColor("#0b141a"));
        root.setPadding(6, 6, 6, 14);
        root.setClipChildren(false); root.setClipToPadding(false);

        HorizontalScrollView sv = new HorizontalScrollView(this);
        sv.setHorizontalScrollBarEnabled(false);
        bar = new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setMinimumHeight(dp(52));
        sv.addView(bar);
        root.addView(sv);

        keyArea = new LinearLayout(this);
        keyArea.setOrientation(LinearLayout.VERTICAL);
        keyArea.setClipChildren(false); keyArea.setClipToPadding(false);
        root.addView(keyArea);
        buildKeys();
        drawBar();
        return root;
    }

    @Override
    public void onStartInputView(EditorInfo info, boolean restarting) {
        super.onStartInputView(info, restarting);
        buf.setLength(0);            // never leak a draft between fields
        shift = false;
        boolean wasAlt = symbols || emoji;
        symbols = false; emoji = false;
        noLearn = isSecure(info);    // no on-device learning in secure fields
        if (wasAlt) buildKeys();
        drawBar();
    }

    private boolean isSecure(EditorInfo info) {
        if (info == null) return false;
        int cls = info.inputType & InputType.TYPE_MASK_CLASS;
        int var = info.inputType & InputType.TYPE_MASK_VARIATION;
        if (cls == InputType.TYPE_CLASS_TEXT) {
            if (var == InputType.TYPE_TEXT_VARIATION_PASSWORD
             || var == InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
             || var == InputType.TYPE_TEXT_VARIATION_WEB_PASSWORD) return true;
        }
        if (cls == InputType.TYPE_CLASS_NUMBER
         && var == InputType.TYPE_NUMBER_VARIATION_PASSWORD) return true;
        return false;
    }

    @Override
    public void onFinishInput() {
        super.onFinishInput();
        flushBuffer();
        engine.endMessage();
        engine.saveState(stateFile);       // persist learning when a field closes
    }

    // ---- key layouts ----------------------------------------------------
    private void buildKeys() {
        keyArea.removeAllViews();
        if (emoji) buildEmoji(); else if (symbols) buildSymbols(); else buildLetters();
    }

    private void buildLetters() {
        keyArea.addView(letterRow(LETTERS[0]));
        keyArea.addView(letterRow(LETTERS[1]));
        LinearLayout r3 = newRow();
        r3.addView(key(shift ? "⇧" : "⇧", 1.5f, this::toggleShift));
        for (char c : LETTERS[2].toCharArray()) { final char ch = c; r3.addView(key(disp(ch), 1f, () -> onLetter(ch))); }
        r3.addView(key("⌫", 1.5f, this::onBackspace, true));
        keyArea.addView(r3);
        LinearLayout r4 = newRow();
        r4.addView(key("123", 1.3f, this::toggleSymbols));
        r4.addView(key("←", 1f, () -> moveCursor(KeyEvent.KEYCODE_DPAD_LEFT), true));
        r4.addView(key("space", 3f, this::onSpace));
        r4.addView(key("→", 1f, () -> moveCursor(KeyEvent.KEYCODE_DPAD_RIGHT), true));
        r4.addView(key("🙂", 1f, this::toggleEmoji));
        r4.addView(key("↵", 1.3f, this::onEnter));
        keyArea.addView(r4);
    }

    private void buildSymbols() {
        keyArea.addView(symRow("1234567890"));           // Latin digits
        keyArea.addView(symRow("၁၂၃၄၅၆၇၈၉၀"));            // Burmese numerals
        LinearLayout r3 = newRow();
        for (String s : new String[]{"။", "၊", ".", ",", "?", "!", "@", "-"})
            r3.addView(key(s, 1f, () -> onSymbol(s)));
        r3.addView(key("⌫", 1.5f, this::onBackspace, true));
        keyArea.addView(r3);
        LinearLayout r4 = newRow();
        r4.addView(key("ABC", 1.3f, this::toggleSymbols));
        r4.addView(key("←", 1f, () -> moveCursor(KeyEvent.KEYCODE_DPAD_LEFT), true));
        r4.addView(key("space", 3f, this::onSpace));
        r4.addView(key("→", 1f, () -> moveCursor(KeyEvent.KEYCODE_DPAD_RIGHT), true));
        r4.addView(key("↵", 1.3f, this::onEnter));
        keyArea.addView(r4);
    }

    private LinearLayout letterRow(String letters) {
        LinearLayout row = newRow();
        for (char c : letters.toCharArray()) { final char ch = c; row.addView(key(disp(ch), 1f, () -> onLetter(ch))); }
        return row;
    }
    private LinearLayout symRow(String chars) {
        LinearLayout row = newRow();
        for (int i = 0; i < chars.length(); i++) {
            final String s = String.valueOf(chars.charAt(i));
            row.addView(key(s, 1f, () -> onSymbol(s)));
        }
        return row;
    }
    private String disp(char ch) { return shift ? String.valueOf(Character.toUpperCase(ch)) : String.valueOf(ch); }
    private LinearLayout newRow() { LinearLayout r = new LinearLayout(this); r.setOrientation(LinearLayout.HORIZONTAL); r.setClipChildren(false); r.setClipToPadding(false); return r; }

    private static final int KEY_BG = Color.parseColor("#2a3942");
    private static final int KEY_BG_DOWN = Color.parseColor("#5b6b75");

    private Button key(String label, float weight, Runnable action) { return key(label, weight, action, false); }

    private Button key(String label, float weight, final Runnable action, final boolean repeatable) {
        Button b = new Button(this);
        b.setText(label); b.setAllCaps(false);
        b.setTextColor(Color.parseColor("#e9edef"));
        b.setBackgroundColor(KEY_BG);
        b.setHapticFeedbackEnabled(true);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, weight);
        lp.setMargins(3, 3, 3, 3); b.setLayoutParams(lp);
        if (!repeatable) b.setOnClickListener(v -> action.run());
        // pop + haptic on touch; repeatable keys fire on press and auto-repeat while held
        b.setOnTouchListener((v, e) -> {
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    v.setBackgroundColor(KEY_BG_DOWN);
                    v.setTranslationZ(dp(8));
                    v.animate().scaleX(1.28f).scaleY(1.28f).translationY(-dp(10)).setDuration(35).start();
                    if (repeatable) { action.run(); startRepeat(action); }
                    break;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    if (repeatable) stopRepeat();
                    v.animate().scaleX(1f).scaleY(1f).translationY(0).setDuration(70)
                     .withEndAction(() -> { v.setBackgroundColor(KEY_BG); v.setTranslationZ(0); }).start();
                    break;
            }
            return repeatable;   // repeatable keys consume (fire on down); others let onClick fire on up
        });
        return b;
    }

    private void startRepeat(final Runnable action) {
        stopRepeat();
        repeatRunnable = () -> { action.run(); if (repeatRunnable != null) repeatHandler.postDelayed(repeatRunnable, 55); };
        repeatHandler.postDelayed(repeatRunnable, 350);   // wait before auto-repeat kicks in
    }
    private void stopRepeat() {
        if (repeatRunnable != null) { repeatHandler.removeCallbacks(repeatRunnable); repeatRunnable = null; }
    }

    private void moveCursor(int keyCode) {
        flushBuffer();                       // commit any pending draft before moving the caret
        InputConnection ic = getCurrentInputConnection();
        if (ic == null) return;
        ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN, keyCode));
        ic.sendKeyEvent(new KeyEvent(KeyEvent.ACTION_UP, keyCode));
    }

    // ---- candidate bar --------------------------------------------------
    private void drawBar() {
        if (bar == null) return;
        bar.removeAllViews();
        if (buf.length() == 0) {
            for (final Engine.Cand c : engine.nextWords())
                bar.addView(candidate(c.word, "", () -> pickWord(c.word)));
            return;
        }
        cands = engine.size() > 0 ? engine.candidates(buf.toString().toLowerCase()) : null;
        if (cands != null) for (final Engine.Cand c : cands)
            bar.addView(candidate(c.word, c.spell, () -> pickWord(c.word)));
        bar.addView(candidate(buf.toString(), "as typed", this::pickRaw));
    }
    private static final int CAND_BG = Color.parseColor("#17232b");
    private static final int CAND_BG_DOWN = Color.parseColor("#356f7d");   // highlight when a word is pressed

    private View candidate(String big, String small, final Runnable action) {
        LinearLayout cell = new LinearLayout(this);
        cell.setOrientation(LinearLayout.VERTICAL);
        cell.setBackgroundColor(CAND_BG);
        cell.setPadding(dp(14), dp(6), dp(14), dp(6));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.setMargins(4, 2, 4, 2); cell.setLayoutParams(lp); cell.setMinimumWidth(dp(56));
        TextView t = new TextView(this); t.setText(big);
        t.setTextColor(Color.parseColor("#e9edef")); t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 19);
        TextView s = new TextView(this); s.setText(small);
        s.setTextColor(Color.parseColor("#8696a0")); s.setTextSize(TypedValue.COMPLEX_UNIT_SP, 10);
        cell.addView(t); cell.addView(s);
        cell.setHapticFeedbackEnabled(true);
        cell.setOnTouchListener((v, e) -> {
            switch (e.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
                    v.setBackgroundColor(CAND_BG_DOWN);
                    break;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    v.postDelayed(() -> v.setBackgroundColor(CAND_BG), 200);   // safety revert if not picked
                    break;
            }
            return false;   // let onClick fire
        });
        // keep the highlight on screen a beat before committing, so the pick is visible
        cell.setOnClickListener(v -> { v.setBackgroundColor(CAND_BG_DOWN); v.postDelayed(action, 110); });
        return cell;
    }

    // ---- input handling -------------------------------------------------
    private void onLetter(char ch) {
        buf.append(shift ? Character.toUpperCase(ch) : ch);
        if (shift) { shift = false; buildKeys(); }
        drawBar();
    }
    private void onSymbol(String s) { flushBuffer(); commit(s); engine.endMessage(); }
    private void toggleShift() { shift = !shift; buildKeys(); }
    private void toggleSymbols() { symbols = !symbols; emoji = false; shift = false; buildKeys(); }
    private static final String[] EMOJI = {
        "😀","😁","😂","🤣","😊","😍","😘","😎",
        "😭","😢","😅","😉","🥰","😴","🤔","😌",
        "👍","👎","🙏","❤","🔥","✨","🎉","💯",
        "😱","👏","🙌","🥳","😜","🤗","🙄","😳"
    };
    private void buildEmoji() {
        for (int r = 0; r < 4; r++) {
            LinearLayout row = newRow();
            for (int c = 0; c < 8; c++) { final String e = EMOJI[r * 8 + c]; row.addView(key(e, 1f, () -> onEmoji(e))); }
            keyArea.addView(row);
        }
        LinearLayout r4 = newRow();
        r4.addView(key("ABC", 1.5f, this::goLetters));
        r4.addView(key("⌫", 1.5f, this::onBackspace, true));
        r4.addView(key("space", 4f, this::onSpace));
        r4.addView(key("↵", 1.5f, this::onEnter));
        keyArea.addView(r4);
    }
    private void onEmoji(String e) { flushBuffer(); commit(e); engine.endMessage(); }
    private void toggleEmoji() { emoji = !emoji; symbols = false; shift = false; buildKeys(); }
    private void goLetters() { emoji = false; symbols = false; shift = false; buildKeys(); }

    private void onBackspace() {
        if (buf.length() > 0) { buf.deleteCharAt(buf.length() - 1); drawBar(); return; }
        InputConnection ic = getCurrentInputConnection();
        if (ic != null) ic.deleteSurroundingText(1, 0);
    }
    private void onSpace() {
        if (buf.length() > 0 && cands != null && !cands.isEmpty()) { pickWord(cands.get(0).word); return; }
        if (buf.length() > 0) { pickRaw(); return; }
        commit(" "); engine.endMessage();
    }
    private void onEnter() { flushBuffer(); commit("\n"); engine.endMessage(); }
    private void flushBuffer() {
        if (buf.length() == 0) return;
        if (cands != null && !cands.isEmpty()) pickWord(cands.get(0).word); else pickRaw();
    }
    private void pickWord(String w) { commit(w); if (!noLearn) engine.learn(w); buf.setLength(0); drawBar(); }
    private void pickRaw() {
        String s = buf.toString();
        commit(s); if (!noLearn) engine.learnRaw(s, s);   // remember the name/word for next time
        buf.setLength(0); drawBar();
    }
    private void commit(String s) {
        InputConnection ic = getCurrentInputConnection();
        if (ic != null) ic.commitText(s, 1);
    }

    private int dp(int v) { return (int) (v * getResources().getDisplayMetrics().density + 0.5f); }
}
