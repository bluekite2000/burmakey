package com.burmakey.ime;

import java.io.BufferedReader;
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
 * The v4 hybrid ranking engine, ported from the tested JS in web-my/ and the
 * Python in src/. Same logic: a multi-spelling lexicon (rule + attested forms),
 * prefix lookup with light variant normalisation, an edit-distance-1 typo
 * fallback, and freq + recency + bigram scoring keyed by WORD (so several
 * spellings of one word share its learned state).
 *
 * No new design here — this is a translation of h2h_v4 / the web keyboard.
 */
public class Engine {
    private final List<String> kk = new ArrayList<>();  // burglish spelling
    private final List<String> lo = new ArrayList<>();  // Burmese word
    private final Map<String, int[]> pref = new HashMap<>();      // prefix -> line ids (cap 50)
    private final Map<String, Integer> widx = new HashMap<>();    // word -> first (best) line
    private final Map<String, Integer> recency = new HashMap<>();
    private final Map<String, Map<String, Integer>> bigram = new HashMap<>();
    private String prev = null;

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
        String line;
        int i = 0;
        while ((line = r.readLine()) != null) {
            int bar = line.indexOf('|');
            if (bar <= 0) continue;
            String sp = line.substring(0, bar);
            String word = line.substring(bar + 1);
            kk.add(sp); lo.add(word);
            if (!widx.containsKey(word)) widx.put(word, i);
            for (int j = 1; j <= sp.length(); j++) {
                String p = sp.substring(0, j);
                List<Integer> l = tmp.computeIfAbsent(p, k -> new ArrayList<>());
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
    public String word(int i) { return lo.get(i); }
    public String spelling(int i) { return kk.get(i); }

    private double score(int i) {
        String w = lo.get(i);
        double s = 1.0 / (i + 2);
        Integer rec = recency.get(w);
        if (rec != null) s += 10.0 * rec;
        if (prev != null) {
            Map<String, Integer> bg = bigram.get(prev);
            if (bg != null) { Integer c = bg.get(w); if (c != null) s += 100.0 * c; }
        }
        return s;
    }

    /** Light variant normalisation, mirroring the web keyboard's norms(). */
    private Set<String> norms(String t) {
        Set<String> out = new LinkedHashSet<>();
        out.add(t);
        String a = t.replace("ph", "hp")
                    .replaceAll("ay", "ei").replaceAll("ai", "ei")
                    .replaceAll("ung\\b", "un").replace("aung", "aun")
                    .replace("ee", "i").replace("oo", "u").replace("aw", "o");
        out.add(a);
        String b = a.replaceAll("([kpmbhtnsgl])y(?=[aeiou])", "$1j").replace("ny", "nj");
        out.add(b);
        return out;
    }

    private List<Integer> fuzzyIds(String t) {
        Set<String> qs = new LinkedHashSet<>();
        for (int i = 0; i < t.length(); i++) {
            String adj = ADJ.get(t.charAt(i));
            if (adj != null)
                for (int k = 0; k < adj.length(); k++)
                    qs.add(t.substring(0, i) + adj.charAt(k) + t.substring(i + 1));
            qs.add(t.substring(0, i) + t.substring(i + 1));            // deletion
            if (i + 1 < t.length())                                   // transposition
                qs.add(t.substring(0, i) + t.charAt(i + 1) + t.charAt(i) + t.substring(i + 2));
        }
        List<Integer> out = new ArrayList<>();
        for (String q : qs)
            for (String v : norms(q)) {
                int[] a = pref.get(v);
                if (a != null) for (int id : a) out.add(id);
            }
        return out;
    }

    /** Top-5 candidate line ids for a typed prefix, deduped by word. */
    public List<Integer> candidates(String txt) {
        List<Integer> ids = new ArrayList<>();
        for (String v : norms(txt)) {
            int[] a = pref.get(v);
            if (a != null) for (int id : a) ids.add(id);
        }
        if (ids.isEmpty() && txt.length() >= 3) ids = fuzzyIds(txt);
        ids.sort((x, y) -> Double.compare(score(y), score(x)));
        Set<String> seen = new LinkedHashSet<>();
        List<Integer> out = new ArrayList<>();
        for (int id : ids) {
            String w = lo.get(id);
            if (seen.contains(w)) continue;
            seen.add(w); out.add(id);
            if (out.size() == 5) break;
        }
        return out;
    }

    public void learn(String word) {
        recency.merge(word, 1, Integer::sum);
        if (prev != null)
            bigram.computeIfAbsent(prev, k -> new HashMap<>()).merge(word, 1, Integer::sum);
        prev = word;
    }

    public void endMessage() { prev = null; }
}
