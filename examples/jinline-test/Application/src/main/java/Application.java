import edu.ucla.cs.onr.test.*;

public class Application {
  public static int doubleOrSquare(int val, boolean doubler) {
    Doer doer;
    if (doubler) {
      doer = new Doubler();
    }
    else {
      doer = new Squarer();
    }
    int result = doer.doIt(val)
    return result;
  }
}
