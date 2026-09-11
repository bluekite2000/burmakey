package com.burmakey.ime;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * The v4 hybrid ranking engine (ported from src/ and web-my/) plus Tier-1
 * on-device learning: recency, bigrams, and a personal vocabulary of words the
 * user committed that no dictionary had (names, slang). All learned state
 * persists to app-private storage and is pruned to a bounded size — nothing
 * leaves the phone. See docs/android-learning.md.
 */
public class Engine {

    public static final class Cand {
        public final String word, spell;
        Cand(String w, String s) { word = w; spell = s; }
    }

    private final List<String> kk = new ArrayList<>();   // lexicon burglish
    private final List<String> lo = new ArrayList<>();   // lexicon Burmese
    private final Map<String, int[]> pref = new HashMap<>();

    // ---- learned state (persisted) ----
    private final Map<String, Integer> recency = new HashMap<>();
    private final Map<String, Map<String, Integer>> bigram = new HashMap<>();
    private final Map<String, Map<String, Integer>> baseBigram = new HashMap<>();  // bundled, not persisted
    private final Map<String, String> syl = new HashMap<>();   // roman syllable -> Burmese (OOV)
    private String[] sylKeys = new String[0];                  // syllable keys, longest first
    private final List<String[]> userList = new ArrayList<>();          // {spell, word}
    private final Map<String, List<Integer>> userPref = new HashMap<>();
    private final Set<String> userSeen = new LinkedHashSet<>();
    private String prev = null;

    private static final int MAX_RECENCY = 3000, MAX_BIGRAM_PAIRS = 20000, MAX_VOCAB = 3000;

    private static final Map<Character, String> ADJ = new HashMap<>();
    static {
        String[][] a = {{"q","wa"},{"w","qes"},{"e","wrd"},{"r","etf"},{"t","ryg"},
            {"y","tuh"},{"u","yij"},{"i","uok"},{"o","ipl"},{"p","ol"},{"a","qsz"},
            {"s","adwx"},{"d","sfec"},{"f","dgrv"},{"g","fhtb"},{"h","gjyn"},
            {"j","hkum"},{"k","jlim"},{"l","ko"},{"z","xas"},{"x","zcsd"},
            {"c","xvdf"},{"v","cbfg"},{"b","vngh"},{"n","bmhj"},{"m","njk"}};
        for (String[] e : a) ADJ.put(e[0].charAt(0), e[1]);
    }

    public void load(InputStream in) throws Exception {
        Map<String, List<Integer>> tmp = new HashMap<>();
        BufferedReader r = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8));
        String line; int i = 0;
        while ((line = r.readLine()) != null) {
            int bar = line.indexOf('|');
            if (bar <= 0) continue;
            String sp = line.substring(0, bar), word = line.substring(bar + 1);
            kk.add(sp); lo.add(word);
            for (int j = 1; j <= sp.length(); j++) {
                List<Integer> l = tmp.computeIfAbsent(sp.substring(0, j), k -> new ArrayList<>());
                if (l.size() < 50) l.add(i);
            }
            i++;
        }
        r.close();
        for (Map.Entry<String, List<Integer>> e : tmp.entrySet()) {
            List<Integer> l = e.getValue();
            int[] arr = new int[l.size()];
            for (int k = 0; k < l.size(); k++) arr[k] = l.get(k);
            pref.put(e.getKey(), arr);
        }
    }

    public int size() { return kk.size(); }

    private double scoreWord(String w, double lexBias) {
        double s = lexBias;
        Integer rec = recency.get(w);
        if (rec != null) s += 10.0 * rec;
        if (prev != null) {
            Map<String, Integer> bg = bigram.get(prev);
            if (bg != null) { Integer c = bg.get(w); if (c != null) s += 100.0 * c; }
        }
        return s;
    }

    private Set<String> norms(String t) {
        Set<String> out = new LinkedHashSet<>();
        out.add(t);
        String a = t.replace("ph", "hp")
                    .replaceAll("ay", "ei").replaceAll("ai", "ei")
                    .replaceAll("ung\\b", "un").replace("aung", "aun")
                    .replace("ee", "i").replace("oo", "u").replace("aw", "o");
        out.add(a);
        out.add(a.replaceAll("([kpmbhtnsgl])y(?=[aeiou])", "$1j").replace("ny", "nj"));
        return out;
    }

    private void collectLex(String prefix, List<Cand> into, Map<String, Double> best) {
        int[] a = pref.get(prefix);
        if (a == null) return;
        for (int id : a) {
            String w = lo.get(id);
            double sc = scoreWord(w, 1.0 / (id + 2));
            Double cur = best.get(w);
            if (cur == null || sc > cur) { best.put(w, sc); }
        }
    }

    /** Top-5 candidates for a typed prefix, lexicon + personal vocab, deduped. */
    public List<Cand> candidates(String txt) {
        Map<String, Double> best = new HashMap<>();
        Map<String, String> spellOf = new HashMap<>();
        // lexicon, through variant normalisation
        for (String v : norms(txt)) {
            int[] a = pref.get(v);
            if (a == null) continue;
            for (int id : a) {
                String w = lo.get(id);
                double sc = scoreWord(w, 1.0 / (id + 2));
                Double cur = best.get(w);
                if (cur == null || sc > cur) { best.put(w, sc); spellOf.put(w, kk.get(id)); }
            }
        }
        // personal vocab (learned words, e.g. names)
        List<Integer> up = userPref.get(txt);
        if (up != null) for (int ui : up) {
            String sp = userList.get(ui)[0], w = userList.get(ui)[1];
            double sc = scoreWord(w, 5.0);              // learned words rank strongly
            Double cur = best.get(w);
            if (cur == null || sc > cur) { best.put(w, sc); spellOf.put(w, sp); }
        }
        // typo fallback only if nothing matched
        if (best.isEmpty() && txt.length() >= 3) {
            for (int id : fuzzyIds(txt)) {
                String w = lo.get(id);
                double sc = scoreWord(w, 0.5 / (id + 2));
                Double cur = best.get(w);
                if (cur == null || sc > cur) { best.put(w, sc); spellOf.put(w, kk.get(id)); }
            }
        }
        List<String> words = new ArrayList<>(best.keySet());
        words.sort((x, y) -> Double.compare(best.get(y), best.get(x)));
        List<Cand> out = new ArrayList<>();
        for (String w : words) { out.add(new Cand(w, spellOf.get(w))); if (out.size() == 5) break; }
        return out;
    }

    private List<Integer> fuzzyIds(String t) {
        Set<String> qs = new LinkedHashSet<>();
        for (int i = 0; i < t.length(); i++) {
            String adj = ADJ.get(t.charAt(i));
            if (adj != null) for (int k = 0; k < adj.length(); k++)
                qs.add(t.substring(0, i) + adj.charAt(k) + t.substring(i + 1));
            qs.add(t.substring(0, i) + t.substring(i + 1));
            if (i + 1 < t.length())
                qs.add(t.substring(0, i) + t.charAt(i + 1) + t.charAt(i) + t.substring(i + 2));
        }
        List<Integer> out = new ArrayList<>();
        for (String q : qs) for (String v : norms(q)) {
            int[] a = pref.get(v);
            if (a != null) for (int id : a) out.add(id);
        }
        return out;
    }

    /** roman-syllable -> Burmese table used to compose out-of-vocabulary words. */
    public void loadSyllables(InputStream in) {
        try (BufferedReader r = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = r.readLine()) != null) {
                int bar = line.indexOf('|');
                if (bar > 0) syl.put(line.substring(0, bar), line.substring(bar + 1));
            }
        } catch (Exception ignored) {}
        List<String> ks = new ArrayList<>(syl.keySet());
        ks.sort((a, b) -> b.length() - a.length());
        sylKeys = ks.toArray(new String[0]);
    }

    // Burglish -> the MLC-ish roman the syllable table is keyed on (order matters)
    private static final String[][] NORM = {
        {"aung","aun"},{"oung","oun"},{"aing","ain"},{"eing","ein"},{"uing","uin"},
        {"oaing","ain"},{"aik","ai"},
        {"uu","u"},{"ee","i"},{"oo","u"},
        {"ay","ei"},{"ai","ei"},
        {"aw","o"},
    };
    private String normOOV(String s) {
        s = s.toLowerCase();
        for (String[] p : NORM) s = s.replace(p[0], p[1]);
        return s;
    }

    /** Compose any Burglish string into Burmese, syllable by syllable (OOV fallback). */
    public String compose(String burglish) {
        if (sylKeys.length == 0 || burglish.isEmpty()) return "";
        String s = normOOV(burglish);
        StringBuilder out = new StringBuilder();
        boolean any = false;
        int i = 0;
        while (i < s.length()) {
            String m = null;
            for (String k : sylKeys) { if (s.startsWith(k, i)) { m = k; break; } }
            if (m != null) { out.append(syl.get(m)); i += m.length(); any = true; }
            else { out.append(s.charAt(i)); i++; }
        }
        return any ? out.toString() : "";
    }

    /** Optional bundled next-word table: "head<tab>next1 next2 ..." ordered by frequency. */
    public void loadBigrams(InputStream in) {
        try (BufferedReader r = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = r.readLine()) != null) {
                int tab = line.indexOf('\t');
                if (tab <= 0) continue;
                String head = line.substring(0, tab);
                String[] nexts = line.substring(tab + 1).trim().split("\\s+");
                Map<String, Integer> m = baseBigram.computeIfAbsent(head, k -> new HashMap<>());
                for (int i = 0; i < nexts.length; i++)
                    if (!nexts[i].isEmpty()) m.put(nexts[i], nexts.length - i);   // earlier = higher
            }
        } catch (Exception ignored) {}
    }

    /** Predicted next words after the last committed word: bundled + personally learned. */
    public List<Cand> nextWords() {
        if (prev == null) return new ArrayList<>();
        Map<String, Integer> merged = new HashMap<>();
        Map<String, Integer> b = baseBigram.get(prev);
        if (b != null) for (Map.Entry<String, Integer> e : b.entrySet()) merged.merge(e.getKey(), e.getValue(), Integer::sum);
        Map<String, Integer> l = bigram.get(prev);
        if (l != null) for (Map.Entry<String, Integer> e : l.entrySet()) merged.merge(e.getKey(), e.getValue() * 8, Integer::sum);
        List<String> ws = new ArrayList<>(merged.keySet());
        ws.sort((x, y) -> Integer.compare(merged.get(y), merged.get(x)));
        List<Cand> out = new ArrayList<>();
        for (String w : ws) { out.add(new Cand(w, "")); if (out.size() == 6) break; }
        return out;
    }

    // ---- learning -------------------------------------------------------
    public void learn(String word) {
        recency.merge(word, 1, Integer::sum);
        if (prev != null)
            bigram.computeIfAbsent(prev, k -> new HashMap<>()).merge(word, 1, Integer::sum);
        prev = word;
    }

    /** A word the lexicon did not offer (a name, slang): remember it. */
    public void learnRaw(String spelling, String word) {
        String key = spelling + "\t" + word;
        if (!userSeen.contains(key) && spelling.length() > 0) {
            userSeen.add(key);
            int idx = userList.size();
            userList.add(new String[]{spelling, word});
            for (int j = 1; j <= spelling.length(); j++)
                userPref.computeIfAbsent(spelling.substring(0, j), k -> new ArrayList<>()).add(idx);
        }
        learn(word);
    }

    public void endMessage() { prev = null; }

    // ---- persistence (app-private file, pruned, never leaves device) ----
    public void loadState(File f) {
        if (!f.exists()) return;
        try (BufferedReader r = new BufferedReader(new InputStreamReader(
                new java.io.FileInputStream(f), StandardCharsets.UTF_8))) {
            String line;
            while ((line = r.readLine()) != null) {
                String[] p = line.split("\t");
                if (p[0].equals("R") && p.length == 3) recency.put(p[1], Integer.parseInt(p[2]));
                else if (p[0].equals("B") && p.length == 4)
                    bigram.computeIfAbsent(p[1], k -> new HashMap<>()).put(p[2], Integer.parseInt(p[3]));
                else if (p[0].equals("V") && p.length == 3) learnRawSilent(p[1], p[2]);
            }
        } catch (Exception ignored) {}
    }

    private void learnRawSilent(String spelling, String word) {
        String key = spelling + "\t" + word;
        if (userSeen.contains(key)) return;
        userSeen.add(key);
        int idx = userList.size();
        userList.add(new String[]{spelling, word});
        for (int j = 1; j <= spelling.length(); j++)
            userPref.computeIfAbsent(spelling.substring(0, j), k -> new ArrayList<>()).add(idx);
    }

    public void saveState(File f) {
        pruneToLimits();
        try (BufferedWriter w = new BufferedWriter(new FileWriter(f))) {
            for (Map.Entry<String, Integer> e : recency.entrySet())
                w.write("R\t" + e.getKey() + "\t" + e.getValue() + "\n");
            for (Map.Entry<String, Map<String, Integer>> e : bigram.entrySet())
                for (Map.Entry<String, Integer> b : e.getValue().entrySet())
                    w.write("B\t" + e.getKey() + "\t" + b.getKey() + "\t" + b.getValue() + "\n");
            for (String[] v : userList) w.write("V\t" + v[0] + "\t" + v[1] + "\n");
        } catch (Exception ignored) {}
    }

    private void pruneToLimits() {
        if (recency.size() > MAX_RECENCY) keepTop(recency, MAX_RECENCY);
        int pairs = 0;
        for (Map<String, Integer> m : bigram.values()) pairs += m.size();
        if (pairs > MAX_BIGRAM_PAIRS) {
            // drop whole low-traffic heads until under the cap; cheap and bounded
            List<String> heads = new ArrayList<>(bigram.keySet());
            heads.sort((x, y) -> Integer.compare(bigram.get(x).size(), bigram.get(y).size()));
            for (String h : heads) {
                if (pairs <= MAX_BIGRAM_PAIRS) break;
                pairs -= bigram.get(h).size(); bigram.remove(h);
            }
        }
        while (userList.size() > MAX_VOCAB) userList.remove(0);   // oldest out
    }

    private void keepTop(Map<String, Integer> m, int n) {
        List<String> ks = new ArrayList<>(m.keySet());
        ks.sort((x, y) -> Integer.compare(m.get(y), m.get(x)));
        for (int i = n; i < ks.size(); i++) m.remove(ks.get(i));
    }

    // test hook
    public int recencyOf(String w) { Integer v = recency.get(w); return v == null ? 0 : v; }
}
