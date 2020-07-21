import edu.ucla.cs.onr.test.*;

public class Application {
  public static int doubleOrSquare(int val, boolean isDouble) {
    Doer doer = null;
    if (isDouble) {
      doer = new Doubler();
    }
    else {
      doer = new Squarer();
    }

    if (val > 100) {
      val = 100;
    }
    else if (val < 0) {
      val = 0;
    }

    int result = doer.doIt(val);
    return result;
  }
}
