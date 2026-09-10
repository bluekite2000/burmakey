import com.burmakey.ime.Engine;
import java.io.*;
import java.util.*;

// Host-JVM test for on-device Tier-1 learning. Run: ./test/run.sh
public class EngineTest {
  static int rankOf(List<Engine.Cand> cs, String word){
    for(int i=0;i<cs.size();i++) if(cs.get(i).word.equals(word)) return i;
    return -1;
  }
  public static void main(String[] a) throws Exception {
    Engine e = new Engine();
    e.load(new FileInputStream("assets/weblex_v4.txt"));
    System.out.println("lexicon size: "+e.size());

    String key="nay";
    List<Engine.Cand> before=e.candidates(key);
    System.out.println("\nBEFORE learning, candidates(\""+key+"\"):");
    for(int i=0;i<before.size();i++) System.out.println("  #"+i+"  "+before.get(i).word+"  ["+before.get(i).spell+"]");

    String target = before.size()>1 ? before.get(1).word : before.get(0).word;
    int r0 = rankOf(before, target);
    System.out.println("\ntarget to promote: "+target+"  (starting rank "+r0+")");

    for(int i=0;i<5;i++) e.learn(target);

    List<Engine.Cand> after=e.candidates(key);
    int r1 = rankOf(after, target);
    System.out.println("AFTER 5 picks, candidates(\""+key+"\"):");
    for(int i=0;i<Math.min(5,after.size());i++) System.out.println("  #"+i+"  "+after.get(i).word+"  ["+after.get(i).spell+"]");
    System.out.println("target rank: "+r0+" -> "+r1+"   recencyOf(target)="+e.recencyOf(target));
    System.out.println(r1==0 ? "PASS promotion: target now rank 0" : "FAIL promotion");

    File tmp=File.createTempFile("learn",".tsv");
    e.saveState(tmp);
    System.out.println("\nsaved state ("+tmp.length()+" bytes):");
    try(BufferedReader br=new BufferedReader(new FileReader(tmp))){
      String ln; int n=0; while((ln=br.readLine())!=null && n++<6) System.out.println("  "+ln);
    }
    Engine e2=new Engine();
    e2.load(new FileInputStream("assets/weblex_v4.txt"));
    e2.loadState(tmp);
    int r2 = rankOf(e2.candidates(key), target);
    System.out.println("reloaded engine: recencyOf(target)="+e2.recencyOf(target)+"  rank="+r2);
    System.out.println(r2==0 && e2.recencyOf(target)>0 ? "PASS persistence: learning survived reload" : "FAIL persistence");

    e2.learnRaw("zzq","ဇက်");
    int r3 = rankOf(e2.candidates("zzq"),"ဇက်");
    System.out.println("\nlearnRaw new word 'zzq'->ဇက် : rank in candidates(\"zzq\") = "+r3);
    System.out.println(r3>=0 ? "PASS learnRaw: personal word is now suggestable" : "FAIL learnRaw");
    tmp.delete();
  }
}
